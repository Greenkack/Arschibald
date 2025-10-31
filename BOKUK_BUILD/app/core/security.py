"""Security & Access Control System - Authentication, Authorization, and Data Protection"""

import hashlib
import hmac
import json
import re
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from .config import get_config
from .database import Base, DatabaseManager, get_db_manager

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    bcrypt = None

try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


# ============================================================================
# Task 9.1: Authentication System
# ============================================================================

class AuthenticationStatus(str, Enum):
    """Authentication status"""
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"
    MFA_REQUIRED = "mfa_required"
    PASSWORD_EXPIRED = "password_expired"


# User-Role association table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(255), ForeignKey('users.id'), primary_key=True),
    Column('role_id', String(255), ForeignKey('roles.id'), primary_key=True)
)


# Role-Permission association table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column(
        'role_id',
        String(255),
        ForeignKey('roles.id'),
        primary_key=True),
    Column(
        'permission_id',
        String(255),
        ForeignKey('permissions.id'),
        primary_key=True))


class User(Base):
    """User model with authentication support"""
    __tablename__ = 'users'

    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime, nullable=True)
    last_failed_login = Column(DateTime, nullable=True)
    locked_until = Column(DateTime, nullable=True)

    # Password management
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    password_expires_at = Column(DateTime, nullable=True)
    must_change_password = Column(Boolean, default=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    sessions = relationship(
        'AuthenticationSession',
        back_populates='user',
        cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Hierarchy
    parent_role_id = Column(String(255), ForeignKey('roles.id'), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship(
        'Permission',
        secondary=role_permissions,
        back_populates='roles')
    parent_role = relationship('Role', remote_side=[id], backref='child_roles')

    def __repr__(self):
        return f"<Role(id='{self.id}', name='{self.name}')>"


class Permission(Base):
    """Permission model for granular access control"""
    __tablename__ = 'permissions'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    resource = Column(String(255), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship(
        'Role',
        secondary=role_permissions,
        back_populates='permissions')

    def __repr__(self):
        return f"<Permission(id='{self.id}', name='{self.name}')>"


class AuthenticationSession(Base):
    """Authentication session model for session management"""
    __tablename__ = 'authentication_sessions'

    id = Column(String(255), primary_key=True)
    user_id = Column(
        String(255),
        ForeignKey('users.id'),
        nullable=False,
        index=True)
    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True)

    # Session data
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship('User', back_populates='sessions')

    def __repr__(self):
        return f"<UserSessionModel(id='{self.id}', user_id='{self.user_id}')>"


class AuthenticationAuditLog(Base):
    """Authentication audit log for security monitoring"""
    __tablename__ = 'authentication_audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    # LOGIN, LOGOUT, FAILED_LOGIN, MFA_SUCCESS, etc.
    event_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)

    # Details
    details = Column(Text, nullable=True)  # JSON

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True)

    def __repr__(self):
        return f"<AuthenticationAuditLog(event='{
            self.event_type}', status='{
            self.status}')>"


@dataclass
class AuthenticationResult:
    """Result of authentication attempt"""
    status: AuthenticationStatus
    user: User | None = None
    session_token: str | None = None
    message: str = ""
    requires_mfa: bool = False
    mfa_token: str | None = None


class PasswordHasher:
    """Secure password hashing with bcrypt"""

    def __init__(self, rounds: int = None):
        if not BCRYPT_AVAILABLE:
            raise ImportError(
                "bcrypt is required for password hashing. Install with: pip install bcrypt")

        config = get_config()
        self.rounds = rounds or config.security.bcrypt_rounds

    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8'))
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
            return False


class MFAManager:
    """Multi-factor authentication manager"""

    def __init__(self):
        if not PYOTP_AVAILABLE:
            logger.warning("pyotp not available, MFA will be disabled")

    def generate_secret(self) -> str:
        """Generate MFA secret"""
        if not PYOTP_AVAILABLE:
            raise ImportError(
                "pyotp is required for MFA. Install with: pip install pyotp")

        return pyotp.random_base32()

    def get_provisioning_uri(
            self,
            secret: str,
            email: str,
            issuer: str = "RobustApp") -> str:
        """Get provisioning URI for QR code"""
        if not PYOTP_AVAILABLE:
            raise ImportError("pyotp is required for MFA")

        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    def verify_token(self, secret: str, token: str) -> bool:
        """Verify MFA token"""
        if not PYOTP_AVAILABLE:
            return False

        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error("MFA verification failed", error=str(e))
            return False


class SessionManager:
    """User session management with configurable timeouts"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()
        self.config = get_config()
        self.session_timeout = self.config.security.session_timeout

    def create_session(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> str:
        """Create new user session"""
        session_token = secrets.token_urlsafe(32)
        session_id = secrets.token_urlsafe(16)

        expires_at = datetime.utcnow() + timedelta(seconds=self.session_timeout)

        session = AuthenticationSession(
            id=session_id,
            user_id=user.id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )

        with self.db_manager.session_scope() as db_session:
            db_session.add(session)

        logger.info("Session created", user_id=user.id, session_id=session_id)

        return session_token

    def validate_session(self, session_token: str) -> User | None:
        """Validate session token and return user"""
        with self.db_manager.session_scope() as db_session:
            session = db_session.query(AuthenticationSession).filter(
                AuthenticationSession.session_token == session_token
            ).first()

            if not session:
                return None

            # Check expiration
            if session.expires_at < datetime.utcnow():
                logger.info("Session expired", session_id=session.id)
                db_session.delete(session)
                return None

            # Update last activity
            session.last_activity = datetime.utcnow()

            # Get user
            user = db_session.query(User).filter(
                User.id == session.user_id).first()

            return user

    def revoke_session(self, session_token: str) -> bool:
        """Revoke session"""
        with self.db_manager.session_scope() as db_session:
            session = db_session.query(AuthenticationSession).filter(
                AuthenticationSession.session_token == session_token
            ).first()

            if session:
                db_session.delete(session)
                logger.info("Session revoked", session_id=session.id)
                return True

            return False

    def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for user"""
        with self.db_manager.session_scope() as db_session:
            count = db_session.query(AuthenticationSession).filter(
                AuthenticationSession.user_id == user_id
            ).delete()

            logger.info(
                "All user sessions revoked",
                user_id=user_id,
                count=count)
            return count

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        with self.db_manager.session_scope() as db_session:
            count = db_session.query(AuthenticationSession).filter(
                AuthenticationSession.expires_at < datetime.utcnow()
            ).delete()

            logger.info("Expired sessions cleaned up", count=count)
            return count


class AuthenticationManager:
    """Comprehensive authentication manager"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()
        self.password_hasher = PasswordHasher()
        self.mfa_manager = MFAManager()
        self.session_manager = SessionManager(db_manager)
        self.config = get_config()

        # Account lockout settings
        self.max_failed_attempts = 5
        self.lockout_duration = 900  # 15 minutes

    def register_user(
        self,
        email: str,
        password: str,
        username: str | None = None,
        full_name: str | None = None,
        **kwargs
    ) -> User:
        """Register new user"""
        # Validate email
        if not self._validate_email(email):
            raise ValueError("Invalid email address")

        # Validate password strength
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet strength requirements")

        # Hash password
        password_hash = self.password_hasher.hash_password(password)

        # Create user
        user_id = secrets.token_urlsafe(16)
        user = User(
            id=user_id,
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            **kwargs
        )

        with self.db_manager.session_scope() as session:
            session.add(user)

        # Log audit
        self._log_auth_event(
            user_id=user_id,
            email=email,
            event_type='REGISTER',
            status='SUCCESS'
        )

        logger.info("User registered", user_id=user_id, email=email)

        return user

    def authenticate(
        self,
        email: str,
        password: str,
        mfa_token: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AuthenticationResult:
        """Authenticate user with password and optional MFA"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.email == email).first()

            if not user:
                self._log_auth_event(
                    email=email,
                    event_type='LOGIN',
                    status='FAILED',
                    details={'reason': 'user_not_found'},
                    ip_address=ip_address
                )
                return AuthenticationResult(
                    status=AuthenticationStatus.FAILED,
                    message="Invalid credentials"
                )

            # Check if account is locked
            if user.is_locked:
                if user.locked_until and user.locked_until > datetime.utcnow():
                    self._log_auth_event(
                        user_id=user.id,
                        email=email,
                        event_type='LOGIN',
                        status='LOCKED',
                        ip_address=ip_address
                    )
                    return AuthenticationResult(
                        status=AuthenticationStatus.LOCKED,
                        message="Account is locked"
                    )
                # Unlock account
                user.is_locked = False
                user.locked_until = None
                user.failed_login_attempts = 0

            # Verify password
            if not self.password_hasher.verify_password(
                    password, user.password_hash):
                user.failed_login_attempts += 1
                user.last_failed_login = datetime.utcnow()

                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.is_locked = True
                    user.locked_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)

                    self._log_auth_event(
                        user_id=user.id,
                        email=email,
                        event_type='ACCOUNT_LOCKED',
                        status='LOCKED',
                        details={
                            'failed_attempts': user.failed_login_attempts},
                        ip_address=ip_address)

                    return AuthenticationResult(
                        status=AuthenticationStatus.LOCKED,
                        message="Account locked due to too many failed attempts")

                self._log_auth_event(
                    user_id=user.id,
                    email=email,
                    event_type='LOGIN',
                    status='FAILED',
                    details={'failed_attempts': user.failed_login_attempts},
                    ip_address=ip_address
                )

                return AuthenticationResult(
                    status=AuthenticationStatus.FAILED,
                    message="Invalid credentials"
                )

            # Check MFA
            if user.mfa_enabled:
                if not mfa_token:
                    # Generate temporary MFA token for session
                    temp_token = secrets.token_urlsafe(32)

                    return AuthenticationResult(
                        status=AuthenticationStatus.MFA_REQUIRED,
                        user=user,
                        mfa_token=temp_token,
                        requires_mfa=True,
                        message="MFA required"
                    )

                # Verify MFA token
                if not self.mfa_manager.verify_token(
                        user.mfa_secret, mfa_token):
                    self._log_auth_event(
                        user_id=user.id,
                        email=email,
                        event_type='MFA_FAILED',
                        status='FAILED',
                        ip_address=ip_address
                    )
                    return AuthenticationResult(
                        status=AuthenticationStatus.FAILED,
                        message="Invalid MFA token"
                    )

                self._log_auth_event(
                    user_id=user.id,
                    email=email,
                    event_type='MFA_SUCCESS',
                    status='SUCCESS',
                    ip_address=ip_address
                )

            # Check password expiration
            if user.password_expires_at and user.password_expires_at < datetime.utcnow():
                return AuthenticationResult(
                    status=AuthenticationStatus.PASSWORD_EXPIRED,
                    user=user,
                    message="Password expired"
                )

            # Reset failed attempts
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()

            # Create session
            session_token = self.session_manager.create_session(
                user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            self._log_auth_event(
                user_id=user.id,
                email=email,
                event_type='LOGIN',
                status='SUCCESS',
                ip_address=ip_address
            )

            logger.info("User authenticated", user_id=user.id, email=email)

            return AuthenticationResult(
                status=AuthenticationStatus.SUCCESS,
                user=user,
                session_token=session_token,
                message="Authentication successful"
            )

    def logout(self, session_token: str) -> bool:
        """Logout user"""
        user = self.session_manager.validate_session(session_token)

        if user:
            self._log_auth_event(
                user_id=user.id,
                email=user.email,
                event_type='LOGOUT',
                status='SUCCESS'
            )

        return self.session_manager.revoke_session(session_token)

    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            # Verify old password
            if not self.password_hasher.verify_password(
                    old_password, user.password_hash):
                self._log_auth_event(
                    user_id=user_id,
                    email=user.email,
                    event_type='PASSWORD_CHANGE',
                    status='FAILED',
                    details={'reason': 'invalid_old_password'}
                )
                return False

            # Validate new password
            if not self._validate_password_strength(new_password):
                raise ValueError(
                    "New password does not meet strength requirements")

            # Hash new password
            user.password_hash = self.password_hasher.hash_password(
                new_password)
            user.password_changed_at = datetime.utcnow()
            user.must_change_password = False

            # Revoke all sessions
            self.session_manager.revoke_all_user_sessions(user_id)

            self._log_auth_event(
                user_id=user_id,
                email=user.email,
                event_type='PASSWORD_CHANGE',
                status='SUCCESS'
            )

            logger.info("Password changed", user_id=user_id)

            return True

    def enable_mfa(self, user_id: str) -> dict[str, str]:
        """Enable MFA for user"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                raise ValueError("User not found")

            # Generate MFA secret
            secret = self.mfa_manager.generate_secret()
            user.mfa_secret = secret
            user.mfa_enabled = True

            # Get provisioning URI
            uri = self.mfa_manager.get_provisioning_uri(secret, user.email)

            self._log_auth_event(
                user_id=user_id,
                email=user.email,
                event_type='MFA_ENABLED',
                status='SUCCESS'
            )

            logger.info("MFA enabled", user_id=user_id)

            return {
                'secret': secret,
                'provisioning_uri': uri
            }

    def disable_mfa(self, user_id: str) -> bool:
        """Disable MFA for user"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            user.mfa_enabled = False
            user.mfa_secret = None

            self._log_auth_event(
                user_id=user_id,
                email=user.email,
                event_type='MFA_DISABLED',
                status='SUCCESS'
            )

            logger.info("MFA disabled", user_id=user_id)

            return True

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        # Minimum 8 characters, at least one uppercase, one lowercase, one
        # digit
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def _log_auth_event(
        self,
        event_type: str,
        status: str,
        user_id: str | None = None,
        email: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        session_id: str | None = None,
        details: dict[str, Any] | None = None
    ):
        """Log authentication event"""
        log_entry = AuthenticationAuditLog(
            user_id=user_id,
            email=email,
            event_type=event_type,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            details=json.dumps(details) if details else None
        )

        with self.db_manager.session_scope() as session:
            session.add(log_entry)


# ============================================================================
# Convenience functions
# ============================================================================

def init_security_tables():
    """Initialize security-related database tables"""
    db_manager = get_db_manager()
    Base.metadata.create_all(bind=db_manager.engine)
    logger.info("Security tables initialized")


def get_authentication_manager() -> AuthenticationManager:
    """Get authentication manager instance"""
    return AuthenticationManager()


def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    return SessionManager()


def get_mfa_manager() -> MFAManager:
    """Get MFA manager instance"""
    return MFAManager()


# ============================================================================
# Task 9.2: Authorization & RBAC
# ============================================================================

class PermissionCache:
    """Cache for permission lookups to improve performance"""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache: dict[str, tuple[set[str], float]] = {}

    def get(self, user_id: str) -> set[str] | None:
        """Get cached permissions"""
        if user_id in self._cache:
            permissions, timestamp = self._cache[user_id]
            if time.time() - timestamp < self.ttl:
                return permissions
            del self._cache[user_id]
        return None

    def set(self, user_id: str, permissions: set[str]):
        """Cache permissions"""
        self._cache[user_id] = (permissions, time.time())

    def invalidate(self, user_id: str = None):
        """Invalidate cache"""
        if user_id:
            self._cache.pop(user_id, None)
        else:
            self._cache.clear()


class AuthorizationManager:
    """Role-based access control with hierarchical roles"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()
        self.permission_cache = PermissionCache()

    def create_role(
        self,
        name: str,
        description: str | None = None,
        parent_role_id: str | None = None
    ) -> Role:
        """Create new role"""
        role_id = secrets.token_urlsafe(16)
        role = Role(
            id=role_id,
            name=name,
            description=description,
            parent_role_id=parent_role_id
        )

        with self.db_manager.session_scope() as session:
            session.add(role)

        logger.info("Role created", role_id=role_id, name=name)

        return role

    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: str | None = None
    ) -> Permission:
        """Create new permission"""
        permission_id = secrets.token_urlsafe(16)
        permission = Permission(
            id=permission_id,
            name=name,
            resource=resource,
            action=action,
            description=description
        )

        with self.db_manager.session_scope() as session:
            session.add(permission)

        logger.info(
            "Permission created",
            permission_id=permission_id,
            name=name)

        return permission

    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign role to user"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            role = session.query(Role).filter(Role.id == role_id).first()

            if not user or not role:
                return False

            if role not in user.roles:
                user.roles.append(role)
                self.permission_cache.invalidate(user_id)
                logger.info(
                    "Role assigned to user",
                    user_id=user_id,
                    role_id=role_id)

            return True

    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove role from user"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            role = session.query(Role).filter(Role.id == role_id).first()

            if not user or not role:
                return False

            if role in user.roles:
                user.roles.remove(role)
                self.permission_cache.invalidate(user_id)
                logger.info(
                    "Role removed from user",
                    user_id=user_id,
                    role_id=role_id)

            return True

    def assign_permission_to_role(
            self,
            role_id: str,
            permission_id: str) -> bool:
        """Assign permission to role"""
        with self.db_manager.session_scope() as session:
            role = session.query(Role).filter(Role.id == role_id).first()
            permission = session.query(Permission).filter(
                Permission.id == permission_id).first()

            if not role or not permission:
                return False

            if permission not in role.permissions:
                role.permissions.append(permission)
                # Invalidate cache for all users with this role
                self.permission_cache.invalidate()
                logger.info(
                    "Permission assigned to role",
                    role_id=role_id,
                    permission_id=permission_id)

            return True

    def remove_permission_from_role(
            self,
            role_id: str,
            permission_id: str) -> bool:
        """Remove permission from role"""
        with self.db_manager.session_scope() as session:
            role = session.query(Role).filter(Role.id == role_id).first()
            permission = session.query(Permission).filter(
                Permission.id == permission_id).first()

            if not role or not permission:
                return False

            if permission in role.permissions:
                role.permissions.remove(permission)
                # Invalidate cache for all users with this role
                self.permission_cache.invalidate()
                logger.info(
                    "Permission removed from role",
                    role_id=role_id,
                    permission_id=permission_id)

            return True

    def get_user_permissions(
            self,
            user_id: str,
            use_cache: bool = True) -> set[str]:
        """Get all permissions for user including inherited from roles"""
        # Check cache first
        if use_cache:
            cached = self.permission_cache.get(user_id)
            if cached is not None:
                return cached

        permissions = set()

        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return permissions

            # Get permissions from all roles (including parent roles)
            for role in user.roles:
                permissions.update(
                    self._get_role_permissions_recursive(
                        role, session))

        # Cache permissions
        if use_cache:
            self.permission_cache.set(user_id, permissions)

        return permissions

    def _get_role_permissions_recursive(self, role: Role, session) -> set[str]:
        """Get permissions for role including parent roles"""
        permissions = {p.name for p in role.permissions}

        # Get permissions from parent role
        if role.parent_role_id:
            parent_role = session.query(Role).filter(
                Role.id == role.parent_role_id).first()
            if parent_role:
                permissions.update(
                    self._get_role_permissions_recursive(
                        parent_role, session))

        return permissions

    def get_user_roles(self, user_id: str) -> list[Role]:
        """Get all roles for user"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return []

            return list(user.roles)

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        return permission in permissions

    def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            return any(role.name == role_name for role in user.roles)

    def check_resource_permission(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> bool:
        """Check if user has permission for specific resource and action"""
        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            # Get all permissions for user
            for role in user.roles:
                permissions = self._get_role_permissions_recursive(
                    role, session)

                # Check if any permission matches resource and action
                for perm_name in permissions:
                    perm = session.query(Permission).filter(
                        Permission.name == perm_name).first()
                    if perm and perm.resource == resource and perm.action == action:
                        return True

            return False

    def evaluate_permission(
        self,
        user_id: str,
        permission_expression: str,
        context: dict[str, Any] | None = None
    ) -> bool:
        """
        Evaluate dynamic permission expression

        Examples:
            - "users:read"
            - "users:write AND users:delete"
            - "admin OR moderator"
        """
        permissions = self.get_user_permissions(user_id)

        # Simple evaluation (can be extended with more complex logic)
        if ' AND ' in permission_expression:
            required = permission_expression.split(' AND ')
            return all(p.strip() in permissions for p in required)
        if ' OR ' in permission_expression:
            options = permission_expression.split(' OR ')
            return any(p.strip() in permissions for p in options)
        return permission_expression in permissions


def require_permission(permission: str):
    """Decorator to require permission for function"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Get user_id from kwargs or context
            user_id = kwargs.get('user_id')
            if not user_id:
                raise PermissionError("User ID required")

            auth_manager = AuthorizationManager()
            if not auth_manager.has_permission(user_id, permission):
                raise PermissionError(f"Permission denied: {permission}")

            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str):
    """Decorator to require role for function"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Get user_id from kwargs or context
            user_id = kwargs.get('user_id')
            if not user_id:
                raise PermissionError("User ID required")

            auth_manager = AuthorizationManager()
            if not auth_manager.has_role(user_id, role):
                raise PermissionError(f"Role required: {role}")

            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Task 9.3: Data Protection System
# ============================================================================

class PIIField(str, Enum):
    """PII field types"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    NAME = "name"
    DATE_OF_BIRTH = "date_of_birth"
    IP_ADDRESS = "ip_address"


class DataProtectionManager:
    """Data protection with PII masking and encryption"""

    def __init__(self):
        self.config = get_config()
        self.secret_key = self.config.security.secret_key.encode('utf-8')

        # PII patterns
        self.pii_patterns = {
            PIIField.EMAIL: r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            PIIField.PHONE: r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            PIIField.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            PIIField.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            PIIField.IP_ADDRESS: r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'}

    def mask_pii(self, text: str, field_type: PIIField = None) -> str:
        """Mask PII in text"""
        if not text:
            return text

        if field_type:
            # Mask specific field type
            pattern = self.pii_patterns.get(field_type)
            if pattern:
                return re.sub(pattern, self._mask_match, text)
        else:
            # Mask all PII types
            for pattern in self.pii_patterns.values():
                text = re.sub(pattern, self._mask_match, text)

        return text

    def _mask_match(self, match) -> str:
        """Mask matched text"""
        text = match.group(0)
        if len(text) <= 4:
            return '*' * len(text)
        # Show first and last 2 characters
        return text[:2] + '*' * (len(text) - 4) + text[-2:]

    def mask_email(self, email: str) -> str:
        """Mask email address"""
        if not email or '@' not in email:
            return email

        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    def mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        if not phone:
            return phone

        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 4:
            return '*' * len(digits)

        # Show last 4 digits
        return '*' * (len(digits) - 4) + digits[-4:]

    def mask_credit_card(self, card: str) -> str:
        """Mask credit card number"""
        if not card:
            return card

        # Remove non-digits
        digits = re.sub(r'\D', '', card)
        if len(digits) < 4:
            return '*' * len(digits)

        # Show last 4 digits
        return '*' * (len(digits) - 4) + digits[-4:]

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        # Simple encryption using HMAC (for production, use proper encryption
        # like Fernet)
        if not data:
            return data

        signature = hmac.new(
            self.secret_key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # In production, use proper encryption
        # For now, just return base64 encoded with signature
        import base64
        encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        return f"{signature}:{encoded}"

    def decrypt_data(self, encrypted: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted or ':' not in encrypted:
            return encrypted

        try:
            signature, encoded = encrypted.split(':', 1)

            import base64
            data = base64.b64decode(encoded).decode('utf-8')

            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if signature != expected_signature:
                raise ValueError("Invalid signature")

            return data
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            return encrypted

    def identify_pii_fields(self, data: dict[str, Any]) -> dict[str, PIIField]:
        """Identify PII fields in data"""
        pii_fields = {}

        for key, value in data.items():
            if not isinstance(value, str):
                continue

            key_lower = key.lower()

            # Check field name
            if 'email' in key_lower:
                pii_fields[key] = PIIField.EMAIL
            elif 'phone' in key_lower or 'mobile' in key_lower:
                pii_fields[key] = PIIField.PHONE
            elif 'ssn' in key_lower or 'social_security' in key_lower:
                pii_fields[key] = PIIField.SSN
            elif 'card' in key_lower or 'credit' in key_lower:
                pii_fields[key] = PIIField.CREDIT_CARD
            elif 'address' in key_lower:
                pii_fields[key] = PIIField.ADDRESS
            elif 'name' in key_lower:
                pii_fields[key] = PIIField.NAME
            elif 'birth' in key_lower or 'dob' in key_lower:
                pii_fields[key] = PIIField.DATE_OF_BIRTH
            elif 'ip' in key_lower:
                pii_fields[key] = PIIField.IP_ADDRESS
            else:
                # Check value patterns
                for field_type, pattern in self.pii_patterns.items():
                    if re.search(pattern, value):
                        pii_fields[key] = field_type
                        break

        return pii_fields

    def mask_dict(self,
                  data: dict[str,
                             Any],
                  pii_fields: dict[str,
                                   PIIField] | None = None) -> dict[str,
                                                                    Any]:
        """Mask PII fields in dictionary"""
        if pii_fields is None:
            pii_fields = self.identify_pii_fields(data)

        masked_data = data.copy()

        for key, field_type in pii_fields.items():
            if key in masked_data:
                value = masked_data[key]
                if isinstance(value, str):
                    if field_type == PIIField.EMAIL:
                        masked_data[key] = self.mask_email(value)
                    elif field_type == PIIField.PHONE:
                        masked_data[key] = self.mask_phone(value)
                    elif field_type == PIIField.CREDIT_CARD:
                        masked_data[key] = self.mask_credit_card(value)
                    else:
                        masked_data[key] = self.mask_pii(value, field_type)

        return masked_data


class DataAccessLog(Base):
    """Data access log for compliance"""
    __tablename__ = 'data_access_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(255), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    action = Column(
        String(50),
        nullable=False,
        index=True)  # READ, WRITE, DELETE

    # Context
    ip_address = Column(String(45), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)

    # PII access
    pii_fields_accessed = Column(Text, nullable=True)  # JSON list

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True)

    def __repr__(self):
        return f"<DataAccessLog(user='{
            self.user_id}', resource='{
            self.resource_type}:{
            self.resource_id}')>"


class DataRetentionPolicy:
    """Data retention policy manager"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()
        self.policies: dict[str, int] = {}  # resource_type -> retention_days

    def set_policy(self, resource_type: str, retention_days: int):
        """Set retention policy for resource type"""
        self.policies[resource_type] = retention_days
        logger.info(
            "Retention policy set",
            resource_type=resource_type,
            retention_days=retention_days)

    def get_policy(self, resource_type: str) -> int | None:
        """Get retention policy for resource type"""
        return self.policies.get(resource_type)

    def cleanup_expired_data(
            self,
            resource_type: str,
            model_class: type) -> int:
        """Clean up expired data based on retention policy"""
        retention_days = self.get_policy(resource_type)
        if not retention_days:
            logger.warning(
                "No retention policy for resource type",
                resource_type=resource_type)
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        with self.db_manager.session_scope() as session:
            # Soft delete if supported
            if hasattr(model_class, 'deleted_at'):
                count = session.query(model_class).filter(
                    model_class.created_at < cutoff_date,
                    model_class.deleted_at.is_(None)
                ).update({'deleted_at': datetime.utcnow()})
            else:
                count = session.query(model_class).filter(
                    model_class.created_at < cutoff_date
                ).delete()

            logger.info(
                "Expired data cleaned up",
                resource_type=resource_type,
                count=count)
            return count


def log_data_access(
    user_id: str,
    resource_type: str,
    resource_id: str,
    action: str,
    pii_fields: list[str] | None = None,
    ip_address: str | None = None,
    session_id: str | None = None
):
    """Log data access for compliance"""
    log_entry = DataAccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        pii_fields_accessed=json.dumps(pii_fields) if pii_fields else None,
        ip_address=ip_address,
        session_id=session_id
    )

    db_manager = get_db_manager()
    with db_manager.session_scope() as session:
        session.add(log_entry)


# ============================================================================
# Convenience functions
# ============================================================================

def get_authorization_manager() -> AuthorizationManager:
    """Get authorization manager instance"""
    return AuthorizationManager()


def get_data_protection_manager() -> DataProtectionManager:
    """Get data protection manager instance"""
    return DataProtectionManager()


def get_data_retention_policy() -> DataRetentionPolicy:
    """Get data retention policy instance"""
    return DataRetentionPolicy()


# ============================================================================
# Task 9.4: Security Monitoring
# ============================================================================

class SecurityEvent(Base):
    """Security event log"""
    __tablename__ = 'security_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(
        String(20),
        nullable=False,
        index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    user_id = Column(String(255), nullable=True, index=True)

    # Event details
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON

    # Context
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)

    # Detection
    # System component that detected the event
    detected_by = Column(String(100), nullable=True)
    threat_score = Column(Integer, default=0)  # 0-100

    # Response
    action_taken = Column(String(255), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(255), nullable=True)

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True)

    def __repr__(self):
        return f"<SecurityEvent(type='{
            self.event_type}', severity='{
            self.severity}')>"


class SecurityEventType(str, Enum):
    """Security event types"""
    FAILED_LOGIN = "failed_login"
    ACCOUNT_LOCKED = "account_locked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    MALICIOUS_REQUEST = "malicious_request"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"


class SecuritySeverity(str, Enum):
    """Security severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatDetector:
    """Threat detection engine"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()

        # Thresholds
        self.failed_login_threshold = 5
        self.failed_login_window = 300  # 5 minutes
        self.suspicious_ip_threshold = 10
        self.suspicious_ip_window = 600  # 10 minutes

    def detect_brute_force(self, email: str, ip_address: str) -> bool:
        """Detect brute force login attempts"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.failed_login_window)

        with self.db_manager.session_scope() as session:
            # Count failed login attempts
            count = session.query(AuthenticationAuditLog).filter(
                AuthenticationAuditLog.email == email,
                AuthenticationAuditLog.event_type == 'LOGIN',
                AuthenticationAuditLog.status == 'FAILED',
                AuthenticationAuditLog.timestamp >= cutoff_time
            ).count()

            return count >= self.failed_login_threshold

    def detect_suspicious_ip(self, ip_address: str) -> bool:
        """Detect suspicious IP activity"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.suspicious_ip_window)

        with self.db_manager.session_scope() as session:
            # Count failed attempts from IP
            count = session.query(AuthenticationAuditLog).filter(
                AuthenticationAuditLog.ip_address == ip_address,
                AuthenticationAuditLog.status == 'FAILED',
                AuthenticationAuditLog.timestamp >= cutoff_time
            ).count()

            return count >= self.suspicious_ip_threshold

    def detect_anomalous_behavior(self, user_id: str) -> dict[str, Any]:
        """Detect anomalous user behavior"""
        anomalies = []

        with self.db_manager.session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return {'anomalies': anomalies, 'threat_score': 0}

            # Check for unusual login times
            if user.last_login:
                hour = user.last_login.hour
                if hour < 6 or hour > 22:
                    anomalies.append({
                        'type': 'unusual_login_time',
                        'description': f'Login at unusual hour: {hour}:00'
                    })

            # Check for multiple failed logins followed by success
            recent_logs = session.query(AuthenticationAuditLog).filter(
                AuthenticationAuditLog.user_id == user_id,
                AuthenticationAuditLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ).order_by(AuthenticationAuditLog.timestamp.desc()).limit(10).all()

            failed_count = sum(
                1 for log in recent_logs if log.status == 'FAILED')
            if failed_count >= 3:
                anomalies.append({
                    'type': 'multiple_failed_attempts',
                    'description': f'{failed_count} failed login attempts in last hour'
                })

            # Calculate threat score
            threat_score = min(len(anomalies) * 25, 100)

            return {
                'anomalies': anomalies,
                'threat_score': threat_score
            }

    def detect_sql_injection(self, input_text: str) -> bool:
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bSELECT\b.*\bFROM\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(--|\#|\/\*)",
            r"(\bOR\b.*=.*)",
            r"(\bAND\b.*=.*)"
        ]

        for pattern in sql_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True

        return False

    def detect_xss(self, input_text: str) -> bool:
        """Detect XSS attempts"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]

        for pattern in xss_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True

        return False


class SecurityMonitor:
    """Security monitoring and alerting system"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()
        self.threat_detector = ThreatDetector(db_manager)
        self.alert_handlers: list[Callable] = []

    def register_alert_handler(self, handler: Callable):
        """Register alert handler"""
        self.alert_handlers.append(handler)

    def log_security_event(
        self,
        event_type: SecurityEventType,
        severity: SecuritySeverity,
        description: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        session_id: str | None = None,
        details: dict[str, Any] | None = None,
        detected_by: str | None = None,
        threat_score: int = 0,
        action_taken: str | None = None
    ) -> SecurityEvent:
        """Log security event"""
        event = SecurityEvent(
            event_type=event_type.value,
            severity=severity.value,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            details=json.dumps(details) if details else None,
            detected_by=detected_by,
            threat_score=threat_score,
            action_taken=action_taken
        )

        with self.db_manager.session_scope() as session:
            session.add(event)

        logger.warning(
            "Security event logged",
            event_type=event_type.value,
            severity=severity.value,
            user_id=user_id
        )

        # Trigger alerts for high severity events
        if severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]:
            self._trigger_alerts(event)

        return event

    def _trigger_alerts(self, event: SecurityEvent):
        """Trigger security alerts"""
        for handler in self.alert_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error("Alert handler failed", error=str(e))

    def monitor_failed_logins(self, email: str, ip_address: str):
        """Monitor failed login attempts"""
        # Check for brute force
        if self.threat_detector.detect_brute_force(email, ip_address):
            self.log_security_event(
                event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
                severity=SecuritySeverity.HIGH,
                description=f"Brute force attempt detected for {email}",
                ip_address=ip_address,
                details={'email': email},
                detected_by='ThreatDetector',
                threat_score=80,
                action_taken='Account locked'
            )

        # Check for suspicious IP
        if self.threat_detector.detect_suspicious_ip(ip_address):
            self.log_security_event(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                severity=SecuritySeverity.MEDIUM,
                description=f"Suspicious activity from IP {ip_address}",
                ip_address=ip_address,
                detected_by='ThreatDetector',
                threat_score=60,
                action_taken='IP flagged for monitoring'
            )

    def monitor_user_activity(self, user_id: str):
        """Monitor user activity for anomalies"""
        result = self.threat_detector.detect_anomalous_behavior(user_id)

        if result['anomalies']:
            self.log_security_event(
                event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                severity=SecuritySeverity.MEDIUM if result['threat_score'] < 50 else SecuritySeverity.HIGH,
                description=f"Anomalous behavior detected for user {user_id}",
                user_id=user_id,
                details={
                    'anomalies': result['anomalies']},
                detected_by='ThreatDetector',
                threat_score=result['threat_score'])

    def validate_input(self, input_text: str, source: str = "unknown") -> bool:
        """Validate input for security threats"""
        # Check for SQL injection
        if self.threat_detector.detect_sql_injection(input_text):
            self.log_security_event(
                event_type=SecurityEventType.SQL_INJECTION_ATTEMPT,
                severity=SecuritySeverity.CRITICAL,
                description=f"SQL injection attempt detected from {source}",
                details={'input': input_text[:100]},
                detected_by='ThreatDetector',
                threat_score=100,
                action_taken='Request blocked'
            )
            return False

        # Check for XSS
        if self.threat_detector.detect_xss(input_text):
            self.log_security_event(
                event_type=SecurityEventType.XSS_ATTEMPT,
                severity=SecuritySeverity.HIGH,
                description=f"XSS attempt detected from {source}",
                details={'input': input_text[:100]},
                detected_by='ThreatDetector',
                threat_score=90,
                action_taken='Request blocked'
            )
            return False

        return True

    def get_security_events(
        self,
        event_type: SecurityEventType | None = None,
        severity: SecuritySeverity | None = None,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        resolved: bool | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[SecurityEvent]:
        """Query security events"""
        with self.db_manager.session_scope() as session:
            query = session.query(SecurityEvent)

            if event_type:
                query = query.filter(
                    SecurityEvent.event_type == event_type.value)

            if severity:
                query = query.filter(SecurityEvent.severity == severity.value)

            if user_id:
                query = query.filter(SecurityEvent.user_id == user_id)

            if start_date:
                query = query.filter(SecurityEvent.timestamp >= start_date)

            if end_date:
                query = query.filter(SecurityEvent.timestamp <= end_date)

            if resolved is not None:
                query = query.filter(SecurityEvent.resolved == resolved)

            query = query.order_by(SecurityEvent.timestamp.desc())
            query = query.limit(limit).offset(offset)

            return query.all()

    def resolve_event(self, event_id: int, resolved_by: str) -> bool:
        """Mark security event as resolved"""
        with self.db_manager.session_scope() as session:
            event = session.query(SecurityEvent).filter(
                SecurityEvent.id == event_id).first()

            if not event:
                return False

            event.resolved = True
            event.resolved_at = datetime.utcnow()
            event.resolved_by = resolved_by

            logger.info(
                "Security event resolved",
                event_id=event_id,
                resolved_by=resolved_by)

            return True

    def get_security_stats(self, days: int = 7) -> dict[str, Any]:
        """Get security statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.db_manager.session_scope() as session:
            # Total events
            total_events = session.query(SecurityEvent).filter(
                SecurityEvent.timestamp >= cutoff_date
            ).count()

            # Events by severity
            events_by_severity = {}
            for severity in SecuritySeverity:
                count = session.query(SecurityEvent).filter(
                    SecurityEvent.timestamp >= cutoff_date,
                    SecurityEvent.severity == severity.value
                ).count()
                events_by_severity[severity.value] = count

            # Events by type
            events_by_type = {}
            for event_type in SecurityEventType:
                count = session.query(SecurityEvent).filter(
                    SecurityEvent.timestamp >= cutoff_date,
                    SecurityEvent.event_type == event_type.value
                ).count()
                if count > 0:
                    events_by_type[event_type.value] = count

            # Unresolved events
            unresolved_events = session.query(SecurityEvent).filter(
                SecurityEvent.timestamp >= cutoff_date,
                SecurityEvent.resolved == False
            ).count()

            # Failed login attempts
            failed_logins = session.query(AuthenticationAuditLog).filter(
                AuthenticationAuditLog.timestamp >= cutoff_date,
                AuthenticationAuditLog.event_type == 'LOGIN',
                AuthenticationAuditLog.status == 'FAILED'
            ).count()

            # Locked accounts
            locked_accounts = session.query(User).filter(
                User.is_locked
            ).count()

            return {
                'period_days': days,
                'total_events': total_events,
                'events_by_severity': events_by_severity,
                'events_by_type': events_by_type,
                'unresolved_events': unresolved_events,
                'failed_logins': failed_logins,
                'locked_accounts': locked_accounts
            }

    def generate_security_report(self, days: int = 30) -> dict[str, Any]:
        """Generate comprehensive security report"""
        stats = self.get_security_stats(days)

        # Get recent critical events
        critical_events = self.get_security_events(
            severity=SecuritySeverity.CRITICAL,
            start_date=datetime.utcnow() - timedelta(days=days),
            limit=10
        )

        # Get top threat IPs
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        with self.db_manager.session_scope() as session:
            top_threat_ips = session.query(
                SecurityEvent.ip_address,
                session.query(SecurityEvent).filter(
                    SecurityEvent.ip_address == SecurityEvent.ip_address
                ).count().label('count')
            ).filter(
                SecurityEvent.timestamp >= cutoff_date,
                SecurityEvent.ip_address.isnot(None)
            ).group_by(SecurityEvent.ip_address).order_by(
                session.query(SecurityEvent).filter(
                    SecurityEvent.ip_address == SecurityEvent.ip_address
                ).count().desc()
            ).limit(10).all()

        return {
            'report_date': datetime.utcnow().isoformat(),
            'period_days': days,
            'statistics': stats,
            'critical_events': [
                {
                    'id': e.id,
                    'type': e.event_type,
                    'description': e.description,
                    'timestamp': e.timestamp.isoformat(),
                    'threat_score': e.threat_score
                }
                for e in critical_events
            ],
            'top_threat_ips': [
                {'ip': ip, 'event_count': count}
                for ip, count in top_threat_ips
            ]
        }


# ============================================================================
# Convenience functions
# ============================================================================

def get_security_monitor() -> SecurityMonitor:
    """Get security monitor instance"""
    return SecurityMonitor()


def get_threat_detector() -> ThreatDetector:
    """Get threat detector instance"""
    return ThreatDetector()


# ============================================================================
# Initialization
# ============================================================================

def init_all_security_tables():
    """Initialize all security-related database tables"""
    db_manager = get_db_manager()
    Base.metadata.create_all(bind=db_manager.engine)
    logger.info("All security tables initialized")


def create_default_roles_and_permissions():
    """Create default roles and permissions"""
    auth_manager = AuthorizationManager()

    # Create default roles
    admin_role = auth_manager.create_role(
        name='admin',
        description='Administrator with full access'
    )

    user_role = auth_manager.create_role(
        name='user',
        description='Standard user with basic access'
    )

    moderator_role = auth_manager.create_role(
        name='moderator',
        description='Moderator with elevated access',
        parent_role_id=user_role.id
    )

    # Create default permissions
    permissions = [
        ('users:read', 'users', 'read', 'Read user information'),
        ('users:write', 'users', 'write', 'Create and update users'),
        ('users:delete', 'users', 'delete', 'Delete users'),
        ('roles:read', 'roles', 'read', 'Read roles'),
        ('roles:write', 'roles', 'write', 'Manage roles'),
        ('permissions:read', 'permissions', 'read', 'Read permissions'),
        ('permissions:write', 'permissions', 'write', 'Manage permissions'),
        ('data:read', 'data', 'read', 'Read data'),
        ('data:write', 'data', 'write', 'Write data'),
        ('data:delete', 'data', 'delete', 'Delete data'),
    ]

    created_permissions = {}
    for name, resource, action, description in permissions:
        perm = auth_manager.create_permission(
            name, resource, action, description)
        created_permissions[name] = perm

    # Assign permissions to roles
    # Admin gets all permissions
    for perm in created_permissions.values():
        auth_manager.assign_permission_to_role(admin_role.id, perm.id)

    # User gets read permissions
    for name, perm in created_permissions.items():
        if ':read' in name:
            auth_manager.assign_permission_to_role(user_role.id, perm.id)

    # Moderator gets read and write for data
    for name, perm in created_permissions.items():
        if name.startswith('data:'):
            auth_manager.assign_permission_to_role(moderator_role.id, perm.id)

    logger.info("Default roles and permissions created")
