"""
Advanced Authentication Service
Implements two-factor authentication, SSO, biometric auth, session management, and password policies
"""

import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.auth_advanced_models import (
    UserTwoFactor, UserSSO, UserBiometric, UserSession, LoginAttempt,
    PasswordPolicy, PasswordHistory, AccountLockout,
    TwoFactorMethod, SSOProvider, BiometricType, AuthMethodType
)
from backend.models.auth_advanced_schemas import *
from backend.core.security import get_password_hash, verify_password
from backend.core.encryption import encrypt_data, decrypt_data


class TwoFactorService:
    """Service for two-factor authentication"""
    
    @staticmethod
    def setup_totp(db: Session, user_id: int) -> Tuple[str, str, List[str]]:
        """
        Setup TOTP (Time-based One-Time Password) for user
        Returns: (secret, qr_code_base64, backup_codes)
        """
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=f"user_{user_id}",
            issuer_name="Solar Calculator Pro"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        # Save to database
        two_factor = UserTwoFactor(
            user_id=user_id,
            method=TwoFactorMethod.TOTP,
            totp_secret=encrypt_data(secret),
            backup_codes=encrypt_data(str(backup_codes)),
            is_enabled=False  # Will be enabled after verification
        )
        db.add(two_factor)
        db.commit()
        
        return secret, qr_code_base64, backup_codes
    
    @staticmethod
    def verify_totp(db: Session, user_id: int, code: str) -> bool:
        """Verify TOTP code"""
        two_factor = db.query(UserTwoFactor).filter(
            and_(
                UserTwoFactor.user_id == user_id,
                UserTwoFactor.method == TwoFactorMethod.TOTP,
                UserTwoFactor.is_enabled == True
            )
        ).first()
        
        if not two_factor:
            return False
        
        secret = decrypt_data(two_factor.totp_secret)
        totp = pyotp.TOTP(secret)
        
        if totp.verify(code, valid_window=1):
            two_factor.last_used_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def setup_sms(db: Session, user_id: int, phone_number: str) -> bool:
        """Setup SMS two-factor authentication"""
        two_factor = UserTwoFactor(
            user_id=user_id,
            method=TwoFactorMethod.SMS,
            phone_number=encrypt_data(phone_number),
            is_enabled=False
        )
        db.add(two_factor)
        db.commit()
        return True
    
    @staticmethod
    def send_sms_code(db: Session, user_id: int) -> str:
        """Send SMS code (returns code for demo, in production would send via SMS gateway)"""
        code = str(secrets.randbelow(1000000)).zfill(6)
        # In production: Send via SMS gateway (Twilio, AWS SNS, etc.)
        return code
    
    @staticmethod
    def verify_backup_code(db: Session, user_id: int, code: str) -> bool:
        """Verify backup code"""
        two_factor = db.query(UserTwoFactor).filter(
            and_(
                UserTwoFactor.user_id == user_id,
                UserTwoFactor.method == TwoFactorMethod.BACKUP_CODES
            )
        ).first()
        
        if not two_factor:
            return False
        
        backup_codes = eval(decrypt_data(two_factor.backup_codes))
        
        if code.upper() in backup_codes:
            backup_codes.remove(code.upper())
            two_factor.backup_codes = encrypt_data(str(backup_codes))
            two_factor.backup_codes_used += 1
            two_factor.last_used_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def enable_two_factor(db: Session, user_id: int, method: TwoFactorMethod) -> bool:
        """Enable two-factor authentication method"""
        two_factor = db.query(UserTwoFactor).filter(
            and_(
                UserTwoFactor.user_id == user_id,
                UserTwoFactor.method == method
            )
        ).first()
        
        if two_factor:
            two_factor.is_enabled = True
            two_factor.verified_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def disable_two_factor(db: Session, user_id: int, method: TwoFactorMethod) -> bool:
        """Disable two-factor authentication method"""
        two_factor = db.query(UserTwoFactor).filter(
            and_(
                UserTwoFactor.user_id == user_id,
                UserTwoFactor.method == method
            )
        ).first()
        
        if two_factor:
            two_factor.is_enabled = False
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_enabled_methods(db: Session, user_id: int) -> List[TwoFactorMethod]:
        """Get list of enabled two-factor methods for user"""
        methods = db.query(UserTwoFactor).filter(
            and_(
                UserTwoFactor.user_id == user_id,
                UserTwoFactor.is_enabled == True
            )
        ).all()
        
        return [m.method for m in methods]


class SSOService:
    """Service for Single Sign-On"""
    
    @staticmethod
    def initiate_oauth(provider: SSOProvider, redirect_uri: str) -> Tuple[str, str]:
        """
        Initiate OAuth flow
        Returns: (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        # Provider-specific OAuth URLs (simplified for demo)
        oauth_urls = {
            SSOProvider.GOOGLE: f"https://accounts.google.com/o/oauth2/v2/auth?state={state}&redirect_uri={redirect_uri}",
            SSOProvider.MICROSOFT: f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?state={state}&redirect_uri={redirect_uri}",
            SSOProvider.GITHUB: f"https://github.com/login/oauth/authorize?state={state}&redirect_uri={redirect_uri}",
        }
        
        return oauth_urls.get(provider, ""), state
    
    @staticmethod
    def link_sso_provider(
        db: Session,
        user_id: int,
        provider: SSOProvider,
        provider_user_id: str,
        provider_email: str,
        access_token: str,
        refresh_token: Optional[str] = None
    ) -> bool:
        """Link SSO provider to user account"""
        sso = UserSSO(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
            access_token=encrypt_data(access_token),
            refresh_token=encrypt_data(refresh_token) if refresh_token else None,
            is_enabled=True
        )
        db.add(sso)
        db.commit()
        return True
    
    @staticmethod
    def unlink_sso_provider(db: Session, user_id: int, provider: SSOProvider) -> bool:
        """Unlink SSO provider from user account"""
        sso = db.query(UserSSO).filter(
            and_(
                UserSSO.user_id == user_id,
                UserSSO.provider == provider
            )
        ).first()
        
        if sso:
            db.delete(sso)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_linked_providers(db: Session, user_id: int) -> List[SSOProvider]:
        """Get list of linked SSO providers for user"""
        providers = db.query(UserSSO).filter(
            and_(
                UserSSO.user_id == user_id,
                UserSSO.is_enabled == True
            )
        ).all()
        
        return [p.provider for p in providers]


class BiometricService:
    """Service for biometric authentication"""
    
    @staticmethod
    def register_biometric(
        db: Session,
        user_id: int,
        biometric_type: BiometricType,
        device_id: str,
        device_name: str,
        device_platform: str,
        public_key: str,
        credential_id: str
    ) -> int:
        """Register biometric authentication for device"""
        biometric = UserBiometric(
            user_id=user_id,
            biometric_type=biometric_type,
            device_id=device_id,
            device_name=device_name,
            device_platform=device_platform,
            public_key=encrypt_data(public_key),
            credential_id=credential_id,
            is_enabled=True
        )
        db.add(biometric)
        db.commit()
        return biometric.id
    
    @staticmethod
    def generate_challenge() -> str:
        """Generate challenge for biometric authentication"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_biometric(
        db: Session,
        device_id: str,
        credential_id: str,
        signature: str,
        challenge: str
    ) -> Optional[int]:
        """
        Verify biometric authentication
        Returns user_id if successful, None otherwise
        """
        biometric = db.query(UserBiometric).filter(
            and_(
                UserBiometric.device_id == device_id,
                UserBiometric.credential_id == credential_id,
                UserBiometric.is_enabled == True
            )
        ).first()
        
        if not biometric:
            return None
        
        # In production: Verify signature using public key and challenge
        # For demo, we'll assume verification succeeds
        
        biometric.last_used_at = datetime.utcnow()
        db.commit()
        
        return biometric.user_id
    
    @staticmethod
    def remove_biometric(db: Session, biometric_id: int) -> bool:
        """Remove biometric authentication"""
        biometric = db.query(UserBiometric).filter(
            UserBiometric.id == biometric_id
        ).first()
        
        if biometric:
            db.delete(biometric)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_registered_devices(db: Session, user_id: int) -> List[dict]:
        """Get list of registered biometric devices"""
        devices = db.query(UserBiometric).filter(
            and_(
                UserBiometric.user_id == user_id,
                UserBiometric.is_enabled == True
            )
        ).all()
        
        return [
            {
                "id": d.id,
                "biometric_type": d.biometric_type.value,
                "device_name": d.device_name,
                "device_platform": d.device_platform,
                "created_at": d.created_at,
                "last_used_at": d.last_used_at
            }
            for d in devices
        ]


class SessionService:
    """Service for session management"""
    
    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        session_token: str,
        refresh_token: str,
        auth_method: AuthMethodType,
        ip_address: str,
        user_agent: str,
        expires_in_hours: int = 24
    ) -> int:
        """Create new user session"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            auth_method=auth_method,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
            is_active=True
        )
        db.add(session)
        db.commit()
        return session.id
    
    @staticmethod
    def get_active_sessions(db: Session, user_id: int) -> List[UserSession]:
        """Get all active sessions for user"""
        return db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).all()
    
    @staticmethod
    def revoke_session(db: Session, session_id: int, reason: str = None) -> bool:
        """Revoke a specific session"""
        session = db.query(UserSession).filter(
            UserSession.id == session_id
        ).first()
        
        if session:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            session.revoked_reason = reason
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def revoke_all_sessions(db: Session, user_id: int, except_session_id: int = None) -> int:
        """Revoke all sessions for user except specified one"""
        query = db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        
        if except_session_id:
            query = query.filter(UserSession.id != except_session_id)
        
        sessions = query.all()
        count = 0
        
        for session in sessions:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            session.revoked_reason = "Revoked by user"
            count += 1
        
        db.commit()
        return count
    
    @staticmethod
    def update_session_activity(db: Session, session_token: str) -> bool:
        """Update last activity time for session"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if session:
            session.last_activity_at = datetime.utcnow()
            db.commit()
            return True
        
        return False


class PasswordPolicyService:
    """Service for password policy management"""
    
    @staticmethod
    def get_active_policy(db: Session) -> Optional[PasswordPolicy]:
        """Get active password policy"""
        return db.query(PasswordPolicy).filter(
            PasswordPolicy.is_active == True
        ).first()
    
    @staticmethod
    def validate_password(password: str, policy: PasswordPolicy) -> Tuple[bool, List[str]]:
        """
        Validate password against policy
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        if len(password) < policy.min_length:
            errors.append(f"Password must be at least {policy.min_length} characters")
        
        if len(password) > policy.max_length:
            errors.append(f"Password must be at most {policy.max_length} characters")
        
        if policy.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if policy.require_special_chars:
            if not any(c in policy.special_chars_allowed for c in password):
                errors.append(f"Password must contain at least one special character: {policy.special_chars_allowed}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def check_password_reuse(db: Session, user_id: int, new_password: str, policy: PasswordPolicy) -> bool:
        """Check if password was recently used"""
        history = db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(PasswordHistory.created_at.desc()).limit(policy.prevent_reuse_count).all()
        
        new_hash = get_password_hash(new_password)
        
        for entry in history:
            if verify_password(new_password, entry.password_hash):
                return True
        
        return False
    
    @staticmethod
    def add_password_to_history(db: Session, user_id: int, password_hash: str):
        """Add password to history"""
        history = PasswordHistory(
            user_id=user_id,
            password_hash=password_hash
        )
        db.add(history)
        db.commit()
    
    @staticmethod
    def check_password_expiry(db: Session, user_id: int, policy: PasswordPolicy) -> Tuple[bool, Optional[int]]:
        """
        Check if password is expired
        Returns: (is_expired, days_until_expiry)
        """
        last_change = db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(PasswordHistory.created_at.desc()).first()
        
        if not last_change:
            return False, None
        
        expiry_date = last_change.created_at + timedelta(days=policy.expires_after_days)
        days_until_expiry = (expiry_date - datetime.utcnow()).days
        
        return days_until_expiry <= 0, days_until_expiry


class LoginAttemptService:
    """Service for tracking login attempts"""
    
    @staticmethod
    def record_attempt(
        db: Session,
        user_id: Optional[int],
        username: str,
        success: bool,
        auth_method: AuthMethodType,
        failure_reason: Optional[str],
        ip_address: str,
        user_agent: str
    ):
        """Record login attempt"""
        attempt = LoginAttempt(
            user_id=user_id,
            username=username,
            success=success,
            auth_method=auth_method,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(attempt)
        db.commit()
    
    @staticmethod
    def get_recent_failed_attempts(db: Session, username: str, minutes: int = 30) -> int:
        """Get count of recent failed login attempts"""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        count = db.query(LoginAttempt).filter(
            and_(
                LoginAttempt.username == username,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at >= since
            )
        ).count()
        
        return count
    
    @staticmethod
    def should_lock_account(db: Session, username: str, policy: PasswordPolicy) -> bool:
        """Check if account should be locked based on failed attempts"""
        failed_count = LoginAttemptService.get_recent_failed_attempts(db, username, 30)
        return failed_count >= policy.max_failed_attempts
    
    @staticmethod
    def lock_account(db: Session, user_id: int, policy: PasswordPolicy, failed_count: int):
        """Lock user account"""
        lockout = AccountLockout(
            user_id=user_id,
            locked_until=datetime.utcnow() + timedelta(minutes=policy.lockout_duration_minutes),
            reason=f"Too many failed login attempts ({failed_count})",
            failed_attempts_count=failed_count,
            is_active=True
        )
        db.add(lockout)
        db.commit()
    
    @staticmethod
    def is_account_locked(db: Session, user_id: int) -> Tuple[bool, Optional[AccountLockout]]:
        """Check if account is currently locked"""
        lockout = db.query(AccountLockout).filter(
            and_(
                AccountLockout.user_id == user_id,
                AccountLockout.is_active == True,
                AccountLockout.locked_until > datetime.utcnow()
            )
        ).first()
        
        return lockout is not None, lockout
    
    @staticmethod
    def unlock_account(db: Session, user_id: int, unlocked_by: int, reason: str):
        """Manually unlock account"""
        lockouts = db.query(AccountLockout).filter(
            and_(
                AccountLockout.user_id == user_id,
                AccountLockout.is_active == True
            )
        ).all()
        
        for lockout in lockouts:
            lockout.is_active = False
            lockout.unlocked_at = datetime.utcnow()
            lockout.unlocked_by = unlocked_by
            lockout.unlock_reason = reason
        
        db.commit()
