"""
Advanced Authentication Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TwoFactorMethodEnum(str, Enum):
    """Two-factor authentication methods"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class SSOProviderEnum(str, Enum):
    """SSO provider types"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    OKTA = "okta"
    CUSTOM_SAML = "custom_saml"
    CUSTOM_OIDC = "custom_oidc"


class BiometricTypeEnum(str, Enum):
    """Biometric authentication types"""
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    WINDOWS_HELLO = "windows_hello"
    TOUCH_ID = "touch_id"


# Two-Factor Authentication Schemas

class TwoFactorSetupRequest(BaseModel):
    """Request to setup two-factor authentication"""
    method: TwoFactorMethodEnum
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None


class TwoFactorSetupResponse(BaseModel):
    """Response with two-factor setup details"""
    method: TwoFactorMethodEnum
    secret: Optional[str] = None  # For TOTP
    qr_code: Optional[str] = None  # Base64 encoded QR code for TOTP
    backup_codes: Optional[List[str]] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


class TwoFactorVerifyRequest(BaseModel):
    """Request to verify two-factor code"""
    method: TwoFactorMethodEnum
    code: str = Field(..., min_length=6, max_length=8)


class TwoFactorVerifyResponse(BaseModel):
    """Response after two-factor verification"""
    verified: bool
    message: str


class TwoFactorDisableRequest(BaseModel):
    """Request to disable two-factor authentication"""
    method: TwoFactorMethodEnum
    password: str


class TwoFactorStatusResponse(BaseModel):
    """Response with two-factor status"""
    enabled: bool
    methods: List[TwoFactorMethodEnum]
    primary_method: Optional[TwoFactorMethodEnum] = None


# SSO Schemas

class SSOInitiateRequest(BaseModel):
    """Request to initiate SSO login"""
    provider: SSOProviderEnum
    redirect_uri: Optional[str] = None


class SSOInitiateResponse(BaseModel):
    """Response with SSO authorization URL"""
    authorization_url: str
    state: str


class SSOCallbackRequest(BaseModel):
    """Request from SSO callback"""
    provider: SSOProviderEnum
    code: str
    state: str


class SSOCallbackResponse(BaseModel):
    """Response after SSO callback"""
    access_token: str
    refresh_token: Optional[str] = None
    user_id: int
    email: str
    name: Optional[str] = None


class SSOLinkRequest(BaseModel):
    """Request to link SSO provider to existing account"""
    provider: SSOProviderEnum
    code: str
    state: str


class SSOUnlinkRequest(BaseModel):
    """Request to unlink SSO provider"""
    provider: SSOProviderEnum
    password: str


class SSOStatusResponse(BaseModel):
    """Response with SSO status"""
    linked_providers: List[SSOProviderEnum]


# Biometric Authentication Schemas

class BiometricRegisterRequest(BaseModel):
    """Request to register biometric authentication"""
    biometric_type: BiometricTypeEnum
    device_id: str
    device_name: Optional[str] = None
    device_platform: Optional[str] = None
    public_key: str
    credential_id: str


class BiometricRegisterResponse(BaseModel):
    """Response after biometric registration"""
    success: bool
    biometric_id: int
    message: str


class BiometricChallengeRequest(BaseModel):
    """Request for biometric challenge"""
    device_id: str


class BiometricChallengeResponse(BaseModel):
    """Response with biometric challenge"""
    challenge: str
    timeout: int = 60


class BiometricVerifyRequest(BaseModel):
    """Request to verify biometric authentication"""
    device_id: str
    credential_id: str
    signature: str
    challenge: str


class BiometricVerifyResponse(BaseModel):
    """Response after biometric verification"""
    verified: bool
    access_token: Optional[str] = None
    message: str


class BiometricRemoveRequest(BaseModel):
    """Request to remove biometric authentication"""
    biometric_id: int
    password: str


class BiometricStatusResponse(BaseModel):
    """Response with biometric status"""
    enabled: bool
    devices: List[dict]


# Session Management Schemas

class SessionInfo(BaseModel):
    """Session information"""
    session_id: int
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_activity_at: datetime
    is_current: bool = False


class SessionListResponse(BaseModel):
    """Response with list of active sessions"""
    sessions: List[SessionInfo]
    total: int


class SessionRevokeRequest(BaseModel):
    """Request to revoke a session"""
    session_id: int
    reason: Optional[str] = None


class SessionRevokeAllRequest(BaseModel):
    """Request to revoke all sessions except current"""
    password: str


# Password Policy Schemas

class PasswordPolicyResponse(BaseModel):
    """Response with password policy"""
    min_length: int
    max_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_numbers: bool
    require_special_chars: bool
    special_chars_allowed: str
    prevent_reuse_count: int
    expires_after_days: int
    warn_before_expiry_days: int
    max_failed_attempts: int
    lockout_duration_minutes: int


class PasswordChangeRequest(BaseModel):
    """Request to change password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v, values):
        """Validate password meets policy requirements"""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v


class PasswordResetRequest(BaseModel):
    """Request to reset password"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Request to confirm password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordExpiryResponse(BaseModel):
    """Response with password expiry information"""
    expires_at: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    is_expired: bool
    requires_change: bool


# Login Attempt Tracking Schemas

class LoginAttemptInfo(BaseModel):
    """Login attempt information"""
    id: int
    username: str
    success: bool
    auth_method: str
    failure_reason: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None
    browser: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    attempted_at: datetime
    is_suspicious: bool


class LoginAttemptsResponse(BaseModel):
    """Response with login attempts"""
    attempts: List[LoginAttemptInfo]
    total: int
    failed_count: int
    suspicious_count: int


class AccountLockoutInfo(BaseModel):
    """Account lockout information"""
    locked_at: datetime
    locked_until: datetime
    reason: str
    failed_attempts_count: int
    is_active: bool


class AccountLockoutResponse(BaseModel):
    """Response with account lockout status"""
    is_locked: bool
    lockout: Optional[AccountLockoutInfo] = None


# Enhanced Login Schemas

class EnhancedLoginRequest(BaseModel):
    """Enhanced login request with multiple auth methods"""
    username: str
    password: Optional[str] = None
    two_factor_code: Optional[str] = None
    two_factor_method: Optional[TwoFactorMethodEnum] = None
    sso_token: Optional[str] = None
    sso_provider: Optional[SSOProviderEnum] = None
    biometric_signature: Optional[str] = None
    biometric_credential_id: Optional[str] = None
    device_id: Optional[str] = None


class EnhancedLoginResponse(BaseModel):
    """Enhanced login response"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    requires_two_factor: bool = False
    available_two_factor_methods: List[TwoFactorMethodEnum] = []
    user_id: Optional[int] = None
    message: str


# Security Event Schemas

class SecurityEventType(str, Enum):
    """Security event types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    TWO_FACTOR_DISABLED = "two_factor_disabled"
    SSO_LINKED = "sso_linked"
    SSO_UNLINKED = "sso_unlinked"
    BIOMETRIC_REGISTERED = "biometric_registered"
    BIOMETRIC_REMOVED = "biometric_removed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    SESSION_REVOKED = "session_revoked"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"


class SecurityEventInfo(BaseModel):
    """Security event information"""
    event_type: SecurityEventType
    timestamp: datetime
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    details: Optional[dict] = None


class SecurityEventsResponse(BaseModel):
    """Response with security events"""
    events: List[SecurityEventInfo]
    total: int
