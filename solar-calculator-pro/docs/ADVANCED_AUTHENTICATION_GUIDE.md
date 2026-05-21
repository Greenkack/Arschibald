# Advanced Authentication System Guide

## Overview

The Advanced Authentication System provides enterprise-grade security features including:

- **Two-Factor Authentication (2FA)**: TOTP, SMS, Email, Backup Codes
- **Single Sign-On (SSO)**: Google, Microsoft, GitHub, Okta, SAML, OIDC
- **Biometric Authentication**: Fingerprint, Face ID, Windows Hello, Touch ID
- **Session Management**: Multi-device session tracking and control
- **Password Policies**: Configurable password requirements and expiration
- **Login Attempt Tracking**: Security monitoring and account lockout

## Table of Contents

1. [Two-Factor Authentication](#two-factor-authentication)
2. [Single Sign-On (SSO)](#single-sign-on-sso)
3. [Biometric Authentication](#biometric-authentication)
4. [Session Management](#session-management)
5. [Password Policies](#password-policies)
6. [Login Attempt Tracking](#login-attempt-tracking)
7. [API Reference](#api-reference)
8. [Security Best Practices](#security-best-practices)

## Two-Factor Authentication

### Supported Methods

#### 1. TOTP (Time-based One-Time Password)

Compatible with Google Authenticator, Authy, Microsoft Authenticator, and other TOTP apps.

**Setup Flow:**
```
1. User requests 2FA setup
2. System generates secret key and QR code
3. User scans QR code with authenticator app
4. User enters verification code
5. System enables 2FA
```

**API Endpoints:**
- `POST /api/v1/auth/advanced/2fa/setup` - Setup TOTP
- `POST /api/v1/auth/advanced/2fa/verify` - Verify TOTP code
- `POST /api/v1/auth/advanced/2fa/disable` - Disable TOTP

**Example Request:**
```json
{
  "method": "totp"
}
```

**Example Response:**
```json
{
  "method": "totp",
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KG...",
  "backup_codes": [
    "A1B2C3D4",
    "E5F6G7H8",
    ...
  ]
}
```

#### 2. SMS Authentication

Send verification codes via SMS.

**Setup Flow:**
```
1. User provides phone number
2. System sends verification code via SMS
3. User enters code
4. System enables SMS 2FA
```

**Requirements:**
- SMS gateway integration (Twilio, AWS SNS, etc.)
- Phone number validation
- Rate limiting for SMS sends

#### 3. Email Authentication

Send verification codes via email.

**Setup Flow:**
```
1. User provides email address
2. System sends verification code via email
3. User enters code
4. System enables email 2FA
```

#### 4. Backup Codes

One-time use backup codes for account recovery.

**Features:**
- 10 backup codes generated during setup
- Each code can only be used once
- Codes are encrypted in database
- User can regenerate codes

### Implementation Example

```python
from backend.services.auth_advanced_service import TwoFactorService

# Setup TOTP
secret, qr_code, backup_codes = TwoFactorService.setup_totp(db, user_id)

# Verify TOTP code
is_valid = TwoFactorService.verify_totp(db, user_id, "123456")

# Enable 2FA
TwoFactorService.enable_two_factor(db, user_id, TwoFactorMethod.TOTP)

# Get enabled methods
methods = TwoFactorService.get_enabled_methods(db, user_id)
```

## Single Sign-On (SSO)

### Supported Providers

1. **Google OAuth 2.0**
2. **Microsoft Azure AD**
3. **GitHub OAuth**
4. **Okta**
5. **Custom SAML 2.0**
6. **Custom OpenID Connect (OIDC)**

### OAuth Flow

```
1. User clicks "Sign in with [Provider]"
2. System redirects to provider authorization URL
3. User authenticates with provider
4. Provider redirects back with authorization code
5. System exchanges code for access token
6. System creates or links user account
7. User is logged in
```

### API Endpoints

- `POST /api/v1/auth/advanced/sso/initiate` - Start SSO flow
- `POST /api/v1/auth/advanced/sso/link` - Link SSO provider to account
- `POST /api/v1/auth/advanced/sso/unlink` - Unlink SSO provider
- `GET /api/v1/auth/advanced/sso/status` - Get linked providers

### Configuration

Each SSO provider requires configuration:

```python
# Google OAuth
GOOGLE_CLIENT_ID = "your-client-id"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_REDIRECT_URI = "http://localhost:3000/auth/sso/callback"

# Microsoft Azure AD
MICROSOFT_CLIENT_ID = "your-client-id"
MICROSOFT_CLIENT_SECRET = "your-client-secret"
MICROSOFT_TENANT_ID = "your-tenant-id"

# GitHub OAuth
GITHUB_CLIENT_ID = "your-client-id"
GITHUB_CLIENT_SECRET = "your-client-secret"
```

### Implementation Example

```python
from backend.services.auth_advanced_service import SSOService

# Initiate OAuth flow
auth_url, state = SSOService.initiate_oauth(
    provider=SSOProvider.GOOGLE,
    redirect_uri="http://localhost:3000/auth/sso/callback"
)

# Link SSO provider
SSOService.link_sso_provider(
    db=db,
    user_id=user_id,
    provider=SSOProvider.GOOGLE,
    provider_user_id="google_user_123",
    provider_email="user@example.com",
    access_token="access_token_here",
    refresh_token="refresh_token_here"
)

# Get linked providers
providers = SSOService.get_linked_providers(db, user_id)
```

## Biometric Authentication

### Supported Types

1. **Fingerprint** - Touch ID, Windows Hello Fingerprint
2. **Face ID** - iOS Face ID, Windows Hello Face
3. **Windows Hello** - Windows biometric authentication
4. **Touch ID** - macOS Touch ID

### WebAuthn Integration

Biometric authentication uses the WebAuthn standard for secure, passwordless authentication.

**Registration Flow:**
```
1. User initiates biometric registration
2. System generates challenge
3. Browser/OS prompts for biometric
4. Device creates credential and signs challenge
5. System stores public key and credential ID
6. Biometric authentication is enabled
```

**Authentication Flow:**
```
1. User initiates biometric login
2. System generates challenge
3. Browser/OS prompts for biometric
4. Device signs challenge with private key
5. System verifies signature with public key
6. User is logged in
```

### API Endpoints

- `POST /api/v1/auth/advanced/biometric/register` - Register biometric
- `POST /api/v1/auth/advanced/biometric/challenge` - Get challenge
- `POST /api/v1/auth/advanced/biometric/verify` - Verify biometric
- `DELETE /api/v1/auth/advanced/biometric/{id}` - Remove biometric
- `GET /api/v1/auth/advanced/biometric/status` - Get registered devices

### Implementation Example

```python
from backend.services.auth_advanced_service import BiometricService

# Register biometric
biometric_id = BiometricService.register_biometric(
    db=db,
    user_id=user_id,
    biometric_type=BiometricType.FINGERPRINT,
    device_id="device_123",
    device_name="iPhone 13",
    device_platform="iOS",
    public_key="public_key_here",
    credential_id="credential_id_here"
)

# Generate challenge
challenge = BiometricService.generate_challenge()

# Verify biometric
user_id = BiometricService.verify_biometric(
    db=db,
    device_id="device_123",
    credential_id="credential_id_here",
    signature="signature_here",
    challenge=challenge
)
```

## Session Management

### Features

- **Multi-device tracking**: Track all active sessions across devices
- **Session details**: IP address, device type, browser, platform
- **Session revocation**: Revoke individual or all sessions
- **Activity tracking**: Last activity timestamp
- **Automatic expiration**: Sessions expire after configured time

### Session Information

Each session stores:
- Session token (JWT)
- Refresh token
- IP address
- User agent
- Device type (desktop, mobile, tablet)
- Device name
- Platform (Windows, macOS, Linux, iOS, Android)
- Browser
- Authentication method used
- Two-factor verification status
- Creation time
- Expiration time
- Last activity time

### API Endpoints

- `GET /api/v1/auth/advanced/sessions` - Get active sessions
- `POST /api/v1/auth/advanced/sessions/revoke` - Revoke session
- `POST /api/v1/auth/advanced/sessions/revoke-all` - Revoke all sessions

### Implementation Example

```python
from backend.services.auth_advanced_service import SessionService

# Create session
session_id = SessionService.create_session(
    db=db,
    user_id=user_id,
    session_token="session_token_here",
    refresh_token="refresh_token_here",
    auth_method=AuthMethodType.TWO_FACTOR,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    expires_in_hours=24
)

# Get active sessions
sessions = SessionService.get_active_sessions(db, user_id)

# Revoke session
SessionService.revoke_session(db, session_id, "User logged out")

# Revoke all sessions except current
count = SessionService.revoke_all_sessions(db, user_id, except_session_id=current_session_id)
```

## Password Policies

### Configurable Requirements

- **Length**: Minimum and maximum password length
- **Character types**: Uppercase, lowercase, numbers, special characters
- **Special characters**: Allowed special characters
- **Password history**: Prevent reusing recent passwords
- **Expiration**: Password expires after N days
- **Warning**: Warn user N days before expiration
- **Lockout**: Lock account after N failed attempts
- **Lockout duration**: Lock account for N minutes

### Default Policy

```
- Minimum length: 8 characters
- Maximum length: 128 characters
- Require uppercase: Yes
- Require lowercase: Yes
- Require numbers: Yes
- Require special characters: Yes
- Special characters: !@#$%^&*()_+-=[]{}|;:,.<>?
- Prevent reuse: Last 5 passwords
- Expires after: 90 days
- Warn before expiry: 7 days
- Max failed attempts: 5
- Lockout duration: 30 minutes
```

### API Endpoints

- `GET /api/v1/auth/advanced/password/policy` - Get password policy
- `POST /api/v1/auth/advanced/password/change` - Change password
- `GET /api/v1/auth/advanced/password/expiry` - Get expiry info

### Implementation Example

```python
from backend.services.auth_advanced_service import PasswordPolicyService

# Get active policy
policy = PasswordPolicyService.get_active_policy(db)

# Validate password
is_valid, errors = PasswordPolicyService.validate_password("MyP@ssw0rd", policy)

# Check password reuse
is_reused = PasswordPolicyService.check_password_reuse(db, user_id, "MyP@ssw0rd", policy)

# Add to password history
PasswordPolicyService.add_password_to_history(db, user_id, password_hash)

# Check password expiry
is_expired, days_until_expiry = PasswordPolicyService.check_password_expiry(db, user_id, policy)
```

## Login Attempt Tracking

### Features

- **Attempt logging**: Record all login attempts (successful and failed)
- **Failure reasons**: Track why login failed
- **Device information**: IP address, device type, browser, platform
- **Geolocation**: Country and city (optional)
- **Suspicious activity detection**: Flag suspicious login attempts
- **Account lockout**: Automatically lock account after failed attempts

### Tracked Information

Each login attempt records:
- User ID (if username exists)
- Username
- Success/failure status
- Authentication method used
- Failure reason
- IP address
- User agent
- Device type
- Platform
- Browser
- Country
- City
- Timestamp
- Suspicious flag
- Blocked flag

### API Endpoints

- `GET /api/v1/auth/advanced/login-attempts` - Get login attempts
- `GET /api/v1/auth/advanced/account/lockout` - Get lockout status

### Implementation Example

```python
from backend.services.auth_advanced_service import LoginAttemptService

# Record login attempt
LoginAttemptService.record_attempt(
    db=db,
    user_id=user_id,
    username="user@example.com",
    success=True,
    auth_method=AuthMethodType.TWO_FACTOR,
    failure_reason=None,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)

# Get recent failed attempts
failed_count = LoginAttemptService.get_recent_failed_attempts(db, "user@example.com", minutes=30)

# Check if should lock account
should_lock = LoginAttemptService.should_lock_account(db, "user@example.com", policy)

# Lock account
LoginAttemptService.lock_account(db, user_id, policy, failed_count)

# Check if account is locked
is_locked, lockout = LoginAttemptService.is_account_locked(db, user_id)

# Unlock account
LoginAttemptService.unlock_account(db, user_id, admin_id, "Manual unlock by admin")
```

## API Reference

### Authentication Headers

All authenticated endpoints require a Bearer token:

```
Authorization: Bearer <access_token>
```

### Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `200 OK` - Success
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Security Best Practices

### 1. Two-Factor Authentication

- **Enable for all users**: Require 2FA for all accounts
- **Multiple methods**: Support multiple 2FA methods for redundancy
- **Backup codes**: Always generate backup codes
- **Rate limiting**: Limit 2FA verification attempts

### 2. Single Sign-On

- **Verify provider**: Always verify SSO provider identity
- **Token validation**: Validate all OAuth tokens
- **Secure storage**: Encrypt access and refresh tokens
- **Token rotation**: Regularly rotate tokens

### 3. Biometric Authentication

- **WebAuthn standard**: Use WebAuthn for biometric auth
- **Challenge-response**: Always use challenge-response protocol
- **Public key storage**: Only store public keys, never private keys
- **Device binding**: Bind biometric to specific device

### 4. Session Management

- **Short expiration**: Use short session expiration times
- **Activity tracking**: Track session activity
- **Revocation**: Allow users to revoke sessions
- **Secure tokens**: Use cryptographically secure tokens

### 5. Password Policies

- **Strong requirements**: Enforce strong password requirements
- **Password history**: Prevent password reuse
- **Regular expiration**: Require periodic password changes
- **Account lockout**: Lock accounts after failed attempts

### 6. Login Attempt Tracking

- **Log all attempts**: Log both successful and failed attempts
- **Monitor suspicious activity**: Flag suspicious login patterns
- **Geolocation tracking**: Track login locations
- **Alert users**: Notify users of suspicious activity

## Deployment Considerations

### Environment Variables

```bash
# Encryption
ENCRYPTION_KEY=your-encryption-key-here

# SSO Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# SMS Gateway (if using SMS 2FA)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Email Service (if using email 2FA)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
```

### Database Migration

Run the migration to create advanced authentication tables:

```bash
alembic upgrade head
```

### Dependencies

Install required Python packages:

```bash
pip install pyotp qrcode cryptography
```

## Support

For issues or questions:
- Documentation: `/docs/ADVANCED_AUTHENTICATION_GUIDE.md`
- API Documentation: `http://localhost:8000/docs`
- Support: support@solarcalculatorpro.com
