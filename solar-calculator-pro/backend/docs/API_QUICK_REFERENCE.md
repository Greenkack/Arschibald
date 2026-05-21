# API Quick Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

### Use Token
```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

### Refresh Token
```bash
POST /api/v1/auth/refresh
Authorization: Bearer YOUR_CURRENT_TOKEN
```

## Common Headers

```http
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
Accept: application/json
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Server Error |

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Authentication | 5/min |
| Read (GET) | 100/min |
| Write (POST/PUT/DELETE) | 50/min |
| Calculations | 20/min |
| PDF Generation | 10/min |
| File Uploads | 5/min |

## Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {},
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Common Error Codes

| Code | Description |
|------|-------------|
| AUTH_001 | Invalid credentials |
| AUTH_002 | Token expired |
| AUTH_003 | Invalid token |
| VAL_001 | Missing required field |
| VAL_002 | Invalid format |
| RES_001 | Resource not found |
| RATE_001 | Rate limit exceeded |

## Pagination

```bash
GET /api/v1/users?page=1&per_page=20
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering & Search

```bash
GET /api/v1/users?search=admin&role=admin&sort=created_at&order=desc
```

## Quick Examples

### Create User
```bash
POST /api/v1/users
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "user"
}
```

### Update User
```bash
PUT /api/v1/users/1
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "email": "newemail@example.com"
}
```

### Delete User
```bash
DELETE /api/v1/users/1
Authorization: Bearer TOKEN
```

### Create Backup
```bash
POST /api/v1/database/backup
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "include_data": true,
  "compress": true
}
```

### Get System Settings
```bash
GET /api/v1/system-settings
Authorization: Bearer TOKEN
```

## Testing with curl

```bash
# Set token variable
TOKEN="your_token_here"

# Make authenticated request
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/users

# POST with data
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"username":"test","email":"test@example.com"}' \
     http://localhost:8000/api/v1/users
```

## Testing with JavaScript

```javascript
const API_URL = 'http://localhost:8000/api/v1';
const token = 'your_token_here';

// GET request
const response = await fetch(`${API_URL}/users`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();

// POST request
const response = await fetch(`${API_URL}/users`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'newuser',
    email: 'user@example.com'
  })
});
```

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
