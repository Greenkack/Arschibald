"""
Advanced Authentication Models
Database models for two-factor authentication, SSO, biometric auth, and session management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class AuthMethodType(str, enum.Enum):
    """Authentication method types"""
    PASSWORD = "password"
    TWO_FACTOR = "two_factor"
    SSO = "sso"
    BIOMETRIC = "biometric"


class TwoFactorMethod(str, enum.Enum):
    """Two-factor authentication methods"""
    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, Authy)
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class SSOProvider(str, enum.Enum):
    """SSO provider types"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    OKTA = "okta"
    CUSTOM_SAML = "custom_saml"
    CUSTOM_OIDC = "custom_oidc"


class BiometricType(str, enum.Enum):
    """Biometric authentication types"""
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    WINDOWS_HELLO = "windows_hello"
    TOUCH_ID = "touch_id"


class UserTwoFactor(Base):
    """Two-factor authentication settings for users"""
    __tablename__ = "user_two_factor"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method = Column(Enum(TwoFactorMethod), nullable=False)
    is_enabled = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)
    
    # TOTP specific
    totp_secret = Column(String(255), nullable=True)  # Encrypted
    
    # SMS/Email specific
    phone_number = Column(String(50), nullable=True)  # Encrypted
    email = Column(String(255), nullable=True)
    
    # Backup codes
    backup_codes = Column(Text, nullable=True)  # Encrypted JSON array
    backup_codes_used = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="two_factor_methods")


class UserSSO(Base):
    """SSO configuration for users"""
    __tablename__ = "user_sso"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(SSOProvider), nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    # Provider-specific identifiers
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    provider_name = Column(String(255), nullable=True)
    
    # OAuth tokens (encrypted)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # SAML/OIDC specific
    saml_name_id = Column(String(255), nullable=True)
    oidc_sub = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sso_providers")


class UserBiometric(Base):
    """Biometric authentication settings for users"""
    __tablename__ = "user_biometric"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    biometric_type = Column(Enum(BiometricType), nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    # Device-specific
    device_id = Column(String(255), nullable=False)
    device_name = Column(String(255), nullable=True)
    device_platform = Column(String(50), nullable=True)  # Windows, macOS, Linux
    
    # Biometric data (encrypted, device-specific)
    public_key = Column(Text, nullable=False)
    credential_id = Column(String(255), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="biometric_methods")


class UserSession(Base):
    """Active user sessions with enhanced tracking"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    device_name = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=True)  # Windows, macOS, Linux
    browser = Column(String(100), nullable=True)
    
    # Authentication method used
    auth_method = Column(Enum(AuthMethodType), nullable=False)
    two_factor_verified = Column(Boolean, default=False)
    
    # Session timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Session status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class LoginAttempt(Base):
    """Track login attempts for security monitoring"""
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for failed username
    username = Column(String(255), nullable=False, index=True)
    
    # Attempt details
    success = Column(Boolean, default=False)
    auth_method = Column(Enum(AuthMethodType), nullable=False)
    failure_reason = Column(String(255), nullable=True)
    
    # Request metadata
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    
    # Geolocation (optional)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Timing
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Security flags
    is_suspicious = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="login_attempts")


class PasswordPolicy(Base):
    """Password policy configuration"""
    __tablename__ = "password_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    
    # Password requirements
    min_length = Column(Integer, default=8)
    max_length = Column(Integer, default=128)
    require_uppercase = Column(Boolean, default=True)
    require_lowercase = Column(Boolean, default=True)
    require_numbers = Column(Boolean, default=True)
    require_special_chars = Column(Boolean, default=True)
    special_chars_allowed = Column(String(100), default="!@#$%^&*()_+-=[]{}|;:,.<>?")
    
    # Password history
    prevent_reuse_count = Column(Integer, default=5)  # Prevent reusing last N passwords
    
    # Password expiration
    expires_after_days = Column(Integer, default=90)
    warn_before_expiry_days = Column(Integer, default=7)
    
    # Account lockout
    max_failed_attempts = Column(Integer, default=5)
    lockout_duration_minutes = Column(Integer, default=30)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PasswordHistory(Base):
    """Track password history for users"""
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="password_history")


class AccountLockout(Base):
    """Track account lockouts"""
    __tablename__ = "account_lockouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Lockout details
    locked_at = Column(DateTime, default=datetime.utcnow)
    locked_until = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=False)
    failed_attempts_count = Column(Integer, default=0)
    
    # Unlock details
    unlocked_at = Column(DateTime, nullable=True)
    unlocked_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin who unlocked
    unlock_reason = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="lockouts")
