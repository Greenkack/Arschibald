# Security Implementation Guide

## Overview

This document describes the comprehensive security implementation for the Solar Calculator Pro Backend API. The security system includes multiple layers of protection against common web vulnerabilities.

## Security Features

### 1. Rate Limiting

**Purpose**: Prevent abuse and ensure fair usage of API resources.

**Implementation**: Using SlowAPI library with configurable limits.

**Features**:
- Global rate limits (200/hour, 50/minute)
- Endpoint-specific limits
- User-based rate limiting (higher limits for authenticated users)
- API key-based rate limiting (for integrations)
- Rate limit headers in responses

**Usage**:

```python
from backend.middleware.rate_limiter import limiter

@app.get("/api/v1/calculate")
@limiter.limit("30/minute")
async def calculate(request: Request):
    # Your endpoint logic
    pass
```

**Configuration**:

```python
# In backend/middleware/rate_limiter.py
class RateLimitConfig:
    GLOBAL_RATE_LIMIT = "200/hour"
    GLOBAL_BURST_LIMIT = "50/minute"
    AUTH_LIMIT = "5/minute"
    CALCULATION_LIMIT = "30/minute"
    DATA_LIMIT = "100/minute"
    UPLOAD_LIMIT = "10/minute"
```

### 2. CSRF Protection

**Purpose**: Prevent Cross-Site Request Forgery attacks.

**Implementation**: Token-based CSRF protection with HMAC signatures.

**Features**:
- Automatic token generation for safe methods (GET, HEAD, OPTIONS)
- Token validation for state-changing methods (POST, PUT, DELETE, PATCH)
- Token expiration (default: 1 hour)
- Secure token storage in httpOnly cookies
- Token rotation after each request

**Usage**:

```python
from backend.middleware.csrf_protection import require_csrf

@app.post("/api/v1/data")
@require_csrf
async def create_data(request: Request, data: dict):
    # Your endpoint logic
    pass
```

**Client Integration**:

```typescript
// Frontend: Include CSRF token in requests
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf_token='))
  ?.split('=')[1];

fetch('/api/v1/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify(data)
});
```

### 3. Input Sanitization

**Purpose**: Prevent injection attacks (SQL, XSS, Command Injection, Path Traversal).

**Implementation**: Pattern-based detection and HTML escaping.

**Features**:
- SQL injection detection
- XSS (Cross-Site Scripting) detection
- Path traversal detection
- Command injection detection
- HTML escaping
- Maximum string/array length enforcement
- Maximum object nesting depth enforcement

**Detected Patterns**:

**SQL Injection**:
- `SELECT * FROM`
- `DROP TABLE`
- `UNION SELECT`
- `' OR '1'='1`
- SQL comments (`--`, `/*`, `*/`)

**XSS**:
- `<script>` tags
- `javascript:` protocol
- Event handlers (`onclick`, `onerror`, etc.)
- `<iframe>`, `<object>`, `<embed>` tags

**Path Traversal**:
- `../` sequences
- URL-encoded traversal (`%2e%2e`)

**Command Injection**:
- Shell operators (`;`, `|`, `&`, `$`)
- Command substitution (`$(...)`, `` `...` ``)

**Usage**:

```python
from backend.middleware.input_sanitizer import sanitize_input

@app.post("/api/v1/data")
@sanitize_input
async def create_data(data: dict):
    # Input is automatically sanitized
    pass
```

### 4. Security Headers

**Purpose**: Protect against various web vulnerabilities through HTTP headers.

**Implementation**: Comprehensive security headers middleware.

**Headers Implemented**:

**Strict-Transport-Security (HSTS)**:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
Forces HTTPS connections for 1 year.

**Content-Security-Policy (CSP)**:
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; ...
```
Controls which resources can be loaded.

**X-Frame-Options**:
```
X-Frame-Options: DENY
```
Prevents clickjacking attacks.

**X-Content-Type-Options**:
```
X-Content-Type-Options: nosniff
```
Prevents MIME type sniffing.

**X-XSS-Protection**:
```
X-XSS-Protection: 1; mode=block
```
Enables browser XSS protection.

**Referrer-Policy**:
```
Referrer-Policy: strict-origin-when-cross-origin
```
Controls referrer information.

**Permissions-Policy**:
```
Permissions-Policy: geolocation=(), camera=(), microphone=(), ...
```
Restricts dangerous browser features.

### 5. SQL Injection Prevention

**Purpose**: Prevent SQL injection attacks.

**Implementation**: Multiple layers of protection.

**Protection Layers**:

1. **SQLAlchemy ORM**: Uses parameterized queries automatically
2. **Input Sanitization**: Detects and blocks SQL injection patterns
3. **Pydantic Validation**: Validates input types and formats

**Best Practices**:

```python
# ✓ GOOD: Using ORM (parameterized)
users = db.query(User).filter(User.username == username).all()

# ✗ BAD: String concatenation (vulnerable)
query = f"SELECT * FROM users WHERE username = '{username}'"
```

## Security Manager

The Security Manager provides a unified interface for all security features.

### Setup

```python
from backend.core.security_manager import setup_security, SecurityPresets

# Production setup (all features enabled)
security_manager = setup_security(app, **SecurityPresets.production())

# Development setup (less strict)
security_manager = setup_security(app, **SecurityPresets.development())

# Testing setup (minimal)
security_manager = setup_security(app, **SecurityPresets.testing())
```

### Security Presets

**Production**:
- Rate Limiting: ✓ Enabled
- CSRF Protection: ✓ Enabled
- Input Sanitization: ✓ Enabled
- Security Headers: ✓ Enabled
- SQL Injection Prevention: ✓ Enabled

**Development**:
- Rate Limiting: ✗ Disabled
- CSRF Protection: ✗ Disabled
- Input Sanitization: ✓ Enabled
- Security Headers: ✗ Disabled
- SQL Injection Prevention: ✓ Enabled

**Testing**:
- Rate Limiting: ✗ Disabled
- CSRF Protection: ✗ Disabled
- Input Sanitization: ✗ Disabled
- Security Headers: ✗ Disabled
- SQL Injection Prevention: ✓ Enabled

### Security Status Endpoint

Check the status of security features:

```bash
GET /security/status
```

Response:
```json
{
  "rate_limiting": {
    "enabled": true,
    "status": "active"
  },
  "csrf_protection": {
    "enabled": true,
    "status": "active"
  },
  "input_sanitization": {
    "enabled": true,
    "status": "active"
  },
  "security_headers": {
    "enabled": true,
    "status": "active"
  },
  "sql_injection_prevention": {
    "enabled": true,
    "status": "active"
  }
}
```

## Configuration

### Environment Variables

```bash
# .env file
SECRET_KEY=your-secret-key-here
DEBUG=false
CORS_ORIGINS=["http://localhost:3000"]
```

### Custom Configuration

```python
from backend.core.security_manager import SecurityManager

security_manager = SecurityManager(
    app=app,
    enable_rate_limiting=True,
    enable_csrf_protection=True,
    enable_input_sanitization=True,
    enable_security_headers=True,
    enable_sql_injection_prevention=True,
)

security_manager.setup_all()
```

## Testing

Run security tests:

```bash
cd backend
pytest tests/test_security.py -v
```

## Best Practices

### 1. Always Use HTTPS in Production

```python
# Enforce HTTPS
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. Keep Dependencies Updated

```bash
pip install --upgrade fastapi uvicorn slowapi
```

### 3. Use Strong Secret Keys

```python
# Generate a strong secret key
import secrets
secret_key = secrets.token_urlsafe(32)
```

### 4. Validate All Input

```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    username: str
    email: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username too short')
        return v
```

### 5. Use Parameterized Queries

```python
# Always use ORM or parameterized queries
users = db.query(User).filter(User.id == user_id).all()
```

### 6. Sanitize Output

```python
import html

# Escape HTML in output
safe_output = html.escape(user_input)
```

### 7. Implement Proper Authentication

```python
from backend.core.auth_dependencies import get_current_user

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.username}
```

### 8. Log Security Events

```python
import logging

logger = logging.getLogger(__name__)

# Log security events
logger.warning(f"Failed login attempt for user: {username}")
logger.error(f"SQL injection detected: {query}")
```

### 9. Regular Security Audits

- Review logs regularly
- Monitor rate limit violations
- Check for suspicious patterns
- Update security configurations

### 10. Principle of Least Privilege

- Grant minimum necessary permissions
- Use role-based access control
- Validate authorization for all operations

## Troubleshooting

### Rate Limit Issues

**Problem**: Legitimate users being rate limited

**Solution**: Increase limits for authenticated users

```python
from backend.middleware.rate_limiter import user_limiter

@app.get("/api/v1/data")
@user_limiter.limit("500/hour")
async def get_data(current_user: User = Depends(get_current_user)):
    pass
```

### CSRF Token Issues

**Problem**: CSRF token validation failing

**Solution**: Ensure token is included in requests

```typescript
// Check if token is present
const csrfToken = getCsrfToken();
if (!csrfToken) {
  // Request new token
  await fetch('/api/v1/csrf-token');
}
```

### Input Sanitization False Positives

**Problem**: Legitimate input being blocked

**Solution**: Adjust sanitization rules or whitelist specific patterns

```python
sanitizer = InputSanitizer(
    enable_sql_check=True,
    enable_xss_check=True,
    enable_path_traversal_check=False,  # Disable if causing issues
)
```

## Security Checklist

- [ ] HTTPS enabled in production
- [ ] Strong secret keys configured
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] Input sanitization enabled
- [ ] Security headers configured
- [ ] SQL injection prevention verified
- [ ] Authentication implemented
- [ ] Authorization implemented
- [ ] Logging configured
- [ ] Regular security audits scheduled
- [ ] Dependencies kept updated
- [ ] Security tests passing

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SlowAPI Documentation](https://slowapi.readthedocs.io/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [HSTS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)

## Support

For security issues or questions, please contact the development team.

**Never disclose security vulnerabilities publicly!**
