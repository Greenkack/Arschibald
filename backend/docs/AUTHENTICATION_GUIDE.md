# Authentication System Guide

## Overview

The authentication system provides secure user authentication, authorization, and session management using JWT (JSON Web Tokens) and bcrypt password hashing.

## Features

- ✅ User registration with strong password validation
- ✅ JWT-based authentication (access and refresh tokens)
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (RBAC)
- ✅ Password change functionality
- ✅ Password reset with tokens
- ✅ User session management
- ✅ Admin user management endpoints
- ✅ OAuth2 password bearer scheme

## Requirements

Implements requirements:
- **1.7**: Backend Service SHALL Authentifizierung und Session-Management implementieren
- **11.1**: Backend Service SHALL Passwörter mit bcrypt hashen
- **11.2**: Backend Service SHALL JWT-Tokens für Authentifizierung verwenden

## Architecture

### Components

1. **Security Module** (`backend/core/security.py`)
   - Password hashing and verification
   - JWT token generation and validation
   - Refresh token management
   - Password reset tokens

2. **Authentication Dependencies** (`backend/core/auth_dependencies.py`)
   - OAuth2 password bearer scheme
   - Current user dependency
   - Role-based access control dependencies

3. **Authentication Service** (`backend/services/auth_service.py`)
   - User registration
   - User authentication
   - Token refresh
   - Password management
   - User management

4. **Authentication API** (`backend/api/v1/auth.py`)
   - REST API endpoints for authentication
   - User management endpoints
   - Admin endpoints

## API Endpoints

### Public Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Protected Endpoints (Require Authentication)

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Update Current User
```http
PUT /api/v1/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Updated Doe",
  "email": "john.updated@example.com"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "SecurePass123",
  "new_password": "NewSecurePass456"
}
```

#### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

#### Get Session Info
```http
GET /api/v1/auth/session
Authorization: Bearer <access_token>
```

### Admin Endpoints (Require Admin Role)

#### List All Users
```http
GET /api/v1/auth/users?skip=0&limit=100
Authorization: Bearer <admin_access_token>
```

#### Get User by ID
```http
GET /api/v1/auth/users/{user_id}
Authorization: Bearer <admin_access_token>
```

#### Update User
```http
PUT /api/v1/auth/users/{user_id}
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "role": "moderator",
  "is_active": true
}
```

#### Deactivate User
```http
POST /api/v1/auth/users/{user_id}/deactivate
Authorization: Bearer <admin_access_token>
```

#### Activate User
```http
POST /api/v1/auth/users/{user_id}/activate
Authorization: Bearer <admin_access_token>
```

## Usage Examples

### Frontend Integration (TypeScript/React)

```typescript
// Login
async function login(username: string, password: string) {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data;
}

// Make authenticated request
async function getProfile() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/v1/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return response.json();
}

// Refresh token
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  const data = await response.json();
  
  // Update tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data;
}
```

### Using Authentication Dependencies

```python
from fastapi import APIRouter, Depends
from backend.core.auth_dependencies import (
    get_current_user,
    get_current_admin_user,
    require_role
)
from backend.models.database_models import User

router = APIRouter()

# Endpoint requiring authentication
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}

# Endpoint requiring admin role
@router.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(get_current_admin_user)):
    return {"message": "Admin access granted"}

# Endpoint requiring specific role
@router.get("/moderator-only")
async def moderator_endpoint(current_user: User = Depends(require_role("moderator"))):
    return {"message": "Moderator access granted"}
```

## Security Features

### Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

### Token Expiration

- **Access Token**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh Token**: 7 days
- **Password Reset Token**: 1 hour

### Password Hashing

- Uses bcrypt algorithm
- Automatic salt generation
- Configurable work factor

### JWT Security

- HS256 algorithm
- Secret key from environment variable
- Token expiration validation
- Token type validation (access vs refresh)

## Configuration

Environment variables in `.env`:

```env
# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing

Run authentication tests:

```bash
cd backend
pytest tests/test_auth.py -v
```

Test coverage includes:
- Password hashing and verification
- JWT token creation and validation
- User registration (success and validation)
- Login (success and error cases)
- Token refresh
- Current user operations
- Password change
- Admin operations
- Role-based access control

## Error Handling

### Common Error Responses

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**
```json
{
  "detail": "Not enough permissions. Admin role required."
}
```

**400 Bad Request**
```json
{
  "detail": "Username already registered"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    }
  ]
}
```

## Best Practices

1. **Token Storage**
   - Store tokens in httpOnly cookies (production)
   - Use localStorage only for development
   - Never store tokens in regular cookies

2. **Token Refresh**
   - Implement automatic token refresh before expiration
   - Handle 401 errors by refreshing token
   - Logout user if refresh token is invalid

3. **Password Security**
   - Never log passwords
   - Use HTTPS in production
   - Implement rate limiting on login endpoint

4. **Role-Based Access**
   - Always verify user role on protected endpoints
   - Use dependency injection for role checks
   - Implement principle of least privilege

## Troubleshooting

### "Could not validate credentials"
- Check if token is expired
- Verify token format (Bearer <token>)
- Ensure SECRET_KEY matches between token creation and validation

### "User not found"
- User may have been deleted
- Check database connection
- Verify username in token payload

### "Inactive user"
- User account has been deactivated
- Contact admin to reactivate account

## Future Enhancements

- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Token blacklisting for logout
- [ ] Session management with Redis
- [ ] Audit logging for authentication events
- [ ] Rate limiting on authentication endpoints
- [ ] Email verification for registration
- [ ] Password reset via email

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Security Guide](./SECURITY_GUIDE.md)
- [Database Setup Guide](./DATABASE_SETUP_GUIDE.md)
