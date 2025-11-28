# Advanced Authentication Quick Reference

## Quick Start

### Enable Two-Factor Authentication

```bash
# Setup TOTP
POST /api/v1/auth/advanced/2fa/setup
{
  "method": "totp"
}

# Verify code
POST /api/v1/auth/advanced/2fa/verify
{
  "method": "totp",
  "code": "123456"
}
```

### Link SSO Provider

```bash
# Initiate SSO
POST /api/v1/auth/advanced/sso/initiate
{
  "provider": "google",
  "redirect_uri": "http://localhost:3000/auth/sso/callback"
}

# Link provider
POST /api/v1/auth/advanced/sso/link
{
  "provider": "google",
  "code": "auth_code_here",
  "state": "state_here"
}
```

### Register Biometric

```bash
# Register
POST /api/v1/auth/advanced/biometric/register
{
  "biometric_type": "fingerprint",
  "device_id": "device_123",
  "device_name": "iPhone 13",
  "device_platform": "iOS",
  "public_key": "public_key_here",
  "credential_id": "credential_id_here"
}

# Verify
POST /api/v1/auth/advanced/biometric/verify
{
  "device_id": "device_123",
  "credential_id": "credential_id_here",
  "signature": "signature_here",
  "challenge": "challenge_here"
}
```

### Manage Sessions

```bash
# Get active sessions
GET /api/v1/auth/advanced/sessions

# Revoke session
POST /api/v1/auth/advanced/sessions/revoke
{
  "session_id": 123,
  "reason": "Logged out"
}

# Revoke all sessions
POST /api/v1/auth/advanced/sessions/revoke-all
{
  "password": "current_password"
}
```

### Change Password

```bash
POST /api/v1/auth/advanced/password/change
{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

### View Login Attempts

```bash
GET /api/v1/auth/advanced/login-attempts?limit=50
```

## API Endpoints Summary

### Two-Factor Authentication
- `POST /api/v1/auth/advanced/2fa/setup` - Setup 2FA
- `POST /api/v1/auth/advanced/2fa/verify` - Verify 2FA code
- `POST /api/v1/auth/advanced/2fa/disable` - Disable 2FA
- `GET /api/v1/auth/advanced/2fa/status` - Get 2FA status

### Single Sign-On
- `POST /api/v1/auth/advanced/sso/initiate` - Start SSO flow
- `POST /api/v1/auth/advanced/sso/link` - Link SSO provider
- `POST /api/v1/auth/advanced/sso/unlink` - Unlink SSO provider
- `GET /api/v1/auth/advanced/sso/status` - Get SSO status

### Biometric Authentication
- `POST /api/v1/auth/advanced/biometric/register` - Register biometric
- `POST /api/v1/auth/advanced/biometric/challenge` - Get challenge
- `POST /api/v1/auth/advanced/biometric/verify` - Verify biometric
- `DELETE /api/v1/auth/advanced/biometric/{id}` - Remove biometric
- `GET /api/v1/auth/advanced/biometric/status` - Get biometric status

### Session Management
- `GET /api/v1/auth/advanced/sessions` - Get active sessions
- `POST /api/v1/auth/advanced/sessions/revoke` - Revoke session
- `POST /api/v1/auth/advanced/sessions/revoke-all` - Revoke all sessions

### Password Management
- `GET /api/v1/auth/advanced/password/policy` - Get password policy
- `POST /api/v1/auth/advanced/password/change` - Change password
- `GET /api/v1/auth/advanced/password/expiry` - Get expiry info

### Security Monitoring
- `GET /api/v1/auth/advanced/login-attempts` - Get login attempts
- `GET /api/v1/auth/advanced/account/lockout` - Get lockout status

## Database Tables

### user_two_factor
- Stores 2FA settings (TOTP secrets, phone numbers, backup codes)

### user_sso
- Stores SSO provider links (Google, Microsoft, GitHub, etc.)

### user_biometric
- Stores biometric credentials (public keys, device info)

### user_sessions
- Tracks active sessions (tokens, device info, activity)

### login_attempts
- Logs all login attempts (success/failure, IP, device)

### password_policies
- Defines password requirements and rules

### password_history
- Tracks password changes for reuse prevention

### account_lockouts
- Manages account lockouts after failed attempts

## Configuration

### Environment Variables

```bash
# Required
ENCRYPTION_KEY=your-encryption-key

# Optional (for SSO)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Optional (for SMS 2FA)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

### Default Password Policy

```
Min length: 8
Max length: 128
Require uppercase: Yes
Require lowercase: Yes
Require numbers: Yes
Require special chars: Yes
Prevent reuse: Last 5 passwords
Expires after: 90 days
Max failed attempts: 5
Lockout duration: 30 minutes
```

## Python Service Examples

### Two-Factor Service

```python
from backend.services.auth_advanced_service import TwoFactorService

# Setup TOTP
secret, qr_code, backup_codes = TwoFactorService.setup_totp(db, user_id)

# Verify TOTP
is_valid = TwoFactorService.verify_totp(db, user_id, "123456")

# Enable 2FA
TwoFactorService.enable_two_factor(db, user_id, TwoFactorMethod.TOTP)
```

### SSO Service

```python
from backend.services.auth_advanced_service import SSOService

# Initiate OAuth
auth_url, state = SSOService.initiate_oauth(SSOProvider.GOOGLE, redirect_uri)

# Link provider
SSOService.link_sso_provider(db, user_id, SSOProvider.GOOGLE, ...)
```

### Biometric Service

```python
from backend.services.auth_advanced_service import BiometricService

# Register biometric
biometric_id = BiometricService.register_biometric(db, user_id, ...)

# Verify biometric
user_id = BiometricService.verify_biometric(db, device_id, ...)
```

### Session Service

```python
from backend.services.auth_advanced_service import SessionService

# Create session
session_id = SessionService.create_session(db, user_id, ...)

# Get active sessions
sessions = SessionService.get_active_sessions(db, user_id)

# Revoke session
SessionService.revoke_session(db, session_id, reason)
```

### Password Policy Service

```python
from backend.services.auth_advanced_service import PasswordPolicyService

# Get policy
policy = PasswordPolicyService.get_active_policy(db)

# Validate password
is_valid, errors = PasswordPolicyService.validate_password(password, policy)

# Check expiry
is_expired, days = PasswordPolicyService.check_password_expiry(db, user_id, policy)
```

### Login Attempt Service

```python
from backend.services.auth_advanced_service import LoginAttemptService

# Record attempt
LoginAttemptService.record_attempt(db, user_id, username, success, ...)

# Check if should lock
should_lock = LoginAttemptService.should_lock_account(db, username, policy)

# Lock account
LoginAttemptService.lock_account(db, user_id, policy, failed_count)
```

## Common Use Cases

### 1. User enables 2FA
```
1. POST /2fa/setup (method: totp)
2. User scans QR code
3. POST /2fa/verify (code from app)
4. 2FA enabled
```

### 2. User logs in with 2FA
```
1. POST /auth/login (username, password)
2. Response: requires_two_factor=true
3. POST /2fa/verify (code from app)
4. Response: access_token
```

### 3. User links Google SSO
```
1. POST /sso/initiate (provider: google)
2. User redirects to Google
3. Google redirects back with code
4. POST /sso/link (code, state)
5. Google account linked
```

### 4. User registers biometric
```
1. POST /biometric/register (device info, public key)
2. Biometric registered
3. User can now login with biometric
```

### 5. User views active sessions
```
1. GET /sessions
2. Response: list of active sessions
3. User can revoke any session
```

### 6. Account gets locked
```
1. User fails login 5 times
2. Account automatically locked for 30 minutes
3. GET /account/lockout shows lockout status
4. Admin can manually unlock
```

## Security Checklist

- [ ] Enable 2FA for all users
- [ ] Configure SSO providers
- [ ] Set strong password policy
- [ ] Enable session tracking
- [ ] Monitor login attempts
- [ ] Configure account lockout
- [ ] Encrypt sensitive data
- [ ] Use HTTPS for all requests
- [ ] Implement rate limiting
- [ ] Regular security audits

## Troubleshooting

### 2FA not working
- Check TOTP secret is correctly stored
- Verify time synchronization
- Check backup codes as fallback

### SSO failing
- Verify OAuth credentials
- Check redirect URI matches
- Validate state parameter

### Biometric not registering
- Check WebAuthn support
- Verify device compatibility
- Check public key format

### Sessions not expiring
- Check expiration time configuration
- Verify cleanup job is running
- Check system time

### Account locked unexpectedly
- Check failed login attempts
- Verify lockout policy settings
- Check for suspicious activity

## Support

- Full Guide: `/docs/ADVANCED_AUTHENTICATION_GUIDE.md`
- API Docs: `http://localhost:8000/docs`
- Issues: GitHub Issues
