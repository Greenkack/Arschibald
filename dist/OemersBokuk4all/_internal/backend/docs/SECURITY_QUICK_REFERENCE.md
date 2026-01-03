# Security Quick Reference

## Quick Setup

```python
from backend.core.security_manager import setup_security, SecurityPresets

# Production
security_manager = setup_security(app, **SecurityPresets.production())

# Development
security_manager = setup_security(app, **SecurityPresets.development())
```

## Rate Limiting

```python
from backend.middleware.rate_limiter import limiter

# Apply rate limit to endpoint
@app.get("/api/v1/data")
@limiter.limit("100/minute")
async def get_data():
    pass

# Different limits for different endpoints
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Stricter for auth
async def login():
    pass
```

## CSRF Protection

```python
from backend.middleware.csrf_protection import require_csrf

# Require CSRF token
@app.post("/api/v1/data")
@require_csrf
async def create_data(request: Request):
    pass

# Exempt from CSRF
@app.post("/api/v1/webhook")
@csrf_exempt
async def webhook():
    pass
```

**Frontend**:
```typescript
// Get CSRF token from cookie
const csrfToken = getCookie('csrf_token');

// Include in request
fetch('/api/v1/data', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken
  }
});
```

## Input Sanitization

```python
from backend.middleware.input_sanitizer import sanitize_input

# Automatic sanitization
@app.post("/api/v1/data")
@sanitize_input
async def create_data(data: dict):
    pass
```

## Security Headers

Automatically applied to all responses:
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Permissions-Policy`

## SQL Injection Prevention

```python
# ✓ GOOD: Use ORM
users = db.query(User).filter(User.id == user_id).all()

# ✗ BAD: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"
```

## Common Patterns

### Protected Endpoint
```python
@app.post("/api/v1/data")
@limiter.limit("30/minute")
@require_csrf
@sanitize_input
async def create_data(
    request: Request,
    data: dict,
    current_user: User = Depends(get_current_user)
):
    # Your logic here
    pass
```

### Public Endpoint
```python
@app.get("/api/v1/public/data")
@limiter.limit("100/minute")
async def get_public_data():
    # Your logic here
    pass
```

### File Upload
```python
@app.post("/api/v1/upload")
@limiter.limit("10/minute")
@require_csrf
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Invalid file type")
    
    # Validate file size
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "File too large")
    
    # Your logic here
    pass
```

## Testing

```bash
# Run security tests
pytest tests/test_security.py -v

# Check security status
curl http://localhost:8000/security/status
```

## Configuration

```python
# Custom rate limits
from backend.middleware.rate_limiter import RateLimitConfig

RateLimitConfig.GLOBAL_RATE_LIMIT = "500/hour"
RateLimitConfig.AUTH_LIMIT = "10/minute"

# Custom CSRF settings
csrf = CSRFProtection(
    secret_key="your-secret",
    token_lifetime=7200,  # 2 hours
)

# Custom sanitization
sanitizer = InputSanitizer(
    enable_sql_check=True,
    enable_xss_check=True,
    max_string_length=5000,
)
```

## Troubleshooting

### Rate Limit Exceeded
```python
# Increase limit for specific endpoint
@app.get("/api/v1/data")
@limiter.limit("200/minute")
async def get_data():
    pass
```

### CSRF Token Missing
```typescript
// Ensure token is sent
const token = getCookie('csrf_token');
if (!token) {
  // Get new token
  await fetch('/api/v1/csrf-token');
}
```

### Input Blocked
```python
# Check logs for details
logger.warning(f"Input blocked: {input_value}")

# Adjust sanitization if needed
sanitizer = InputSanitizer(
    enable_path_traversal_check=False
)
```

## Security Checklist

- [ ] HTTPS in production
- [ ] Strong secret keys
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] Input sanitization enabled
- [ ] Security headers configured
- [ ] Authentication implemented
- [ ] Authorization implemented
- [ ] Logging configured
- [ ] Tests passing

## Emergency Response

### Suspected Attack
1. Check logs: `tail -f logs/app.log`
2. Check rate limits: `GET /security/status`
3. Block IP if needed
4. Review recent changes
5. Update security rules

### Security Incident
1. Document the incident
2. Isolate affected systems
3. Analyze attack vector
4. Apply fixes
5. Update security measures
6. Notify stakeholders

## Resources

- Full Guide: `backend/docs/SECURITY_GUIDE.md`
- Tests: `backend/tests/test_security.py`
- Code: `backend/middleware/` and `backend/core/security_manager.py`
