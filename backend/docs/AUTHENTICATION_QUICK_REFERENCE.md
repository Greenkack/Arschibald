# Authentication Quick Reference

## Quick Start

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Use Access Token
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Common Operations

### Get Current User Info
```python
from backend.core.auth_dependencies import get_current_user

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

### Require Admin Role
```python
from backend.core.auth_dependencies import get_current_admin_user

@router.get("/admin")
async def admin_only(user: User = Depends(get_current_admin_user)):
    return {"message": "Admin access"}
```

### Require Specific Role
```python
from backend.core.auth_dependencies import require_role

@router.get("/moderator")
async def moderator_only(user: User = Depends(require_role("moderator"))):
    return {"message": "Moderator access"}
```

## Password Requirements

✅ Minimum 8 characters  
✅ At least one uppercase letter  
✅ At least one lowercase letter  
✅ At least one digit  

## Token Expiration

| Token Type | Expiration |
|------------|------------|
| Access Token | 30 minutes |
| Refresh Token | 7 days |
| Password Reset | 1 hour |

## API Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | No | Register new user |
| `/api/v1/auth/login` | POST | No | Login and get tokens |
| `/api/v1/auth/refresh` | POST | No | Refresh access token |
| `/api/v1/auth/logout` | POST | Yes | Logout (client-side) |
| `/api/v1/auth/me` | GET | Yes | Get current user |
| `/api/v1/auth/me` | PUT | Yes | Update current user |
| `/api/v1/auth/change-password` | POST | Yes | Change password |
| `/api/v1/auth/session` | GET | Yes | Get session info |
| `/api/v1/auth/users` | GET | Admin | List all users |
| `/api/v1/auth/users/{id}` | GET | Admin | Get user by ID |
| `/api/v1/auth/users/{id}` | PUT | Admin | Update user |
| `/api/v1/auth/users/{id}/deactivate` | POST | Admin | Deactivate user |
| `/api/v1/auth/users/{id}/activate` | POST | Admin | Activate user |

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created (registration) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid credentials) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation) |

## Environment Variables

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing

```bash
# Run all auth tests
pytest backend/tests/test_auth.py -v

# Run specific test
pytest backend/tests/test_auth.py::test_login_success -v

# Run with coverage
pytest backend/tests/test_auth.py --cov=backend.core.security --cov=backend.services.auth_service
```

## Common Issues

### "Could not validate credentials"
→ Token expired or invalid. Refresh token or login again.

### "Username already registered"
→ Choose a different username.

### "Incorrect username or password"
→ Check credentials and try again.

### "Not enough permissions"
→ Endpoint requires admin role or specific role.

## Security Checklist

- [x] Passwords hashed with bcrypt
- [x] JWT tokens with expiration
- [x] Role-based access control
- [x] Password strength validation
- [x] Inactive user check
- [x] Token refresh mechanism
- [x] Secure token storage (client-side)
- [x] HTTPS in production

## Next Steps

1. Implement frontend authentication
2. Add token refresh logic
3. Implement logout on client
4. Add role-based UI components
5. Set up password reset emails
6. Add 2FA (future enhancement)
