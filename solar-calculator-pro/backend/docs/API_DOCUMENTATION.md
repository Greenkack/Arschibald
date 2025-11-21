# Solar Calculator Pro - API Documentation

## Overview

The Solar Calculator Pro API is a RESTful API built with FastAPI that provides comprehensive backend services for the Solar Calculator Pro desktop application. This API handles solar calculations, heat pump analysis, price matrix management, PDF generation, CRM operations, and more.

**Base URL:** `http://localhost:8000/api/v1`

**API Version:** 1.0.0

**Content Type:** `application/json`

## Table of Contents

1. [Authentication](#authentication)
2. [Error Handling](#error-handling)
3. [Rate Limiting](#rate-limiting)
4. [Endpoints](#endpoints)
5. [Request/Response Examples](#examples)
6. [Error Codes](#error-codes)
7. [Best Practices](#best-practices)

---

## Authentication

### Overview

The API uses JWT (JSON Web Token) based authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Authentication Flow

```
1. Client sends credentials to /api/v1/auth/login
2. Server validates credentials and returns JWT token
3. Client includes token in subsequent requests
4. Server validates token and processes request
```

### Obtaining a Token

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```


### Using the Token

Include the token in the Authorization header for all protected endpoints:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example with curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://localhost:8000/api/v1/projects
```

**Example with JavaScript:**
```javascript
fetch('http://localhost:8000/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Token Expiration

- **Default Expiration:** 1 hour (3600 seconds)
- **Refresh:** Use `/api/v1/auth/refresh` endpoint before expiration
- **Expired Token Response:** HTTP 401 Unauthorized

### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Headers:**
```http
Authorization: Bearer YOUR_CURRENT_TOKEN
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context",
      "path": "/api/v1/endpoint"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```


### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

### Overview

The API implements rate limiting to prevent abuse and ensure fair usage. Rate limits are applied per IP address and per authenticated user.

### Rate Limit Headers

Every API response includes rate limit information in the headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

- **X-RateLimit-Limit:** Maximum requests allowed in the time window
- **X-RateLimit-Remaining:** Requests remaining in current window
- **X-RateLimit-Reset:** Unix timestamp when the limit resets

### Rate Limits by Endpoint Category

| Category | Limit | Window |
|----------|-------|--------|
| Authentication | 5 requests | 1 minute |
| Read Operations (GET) | 100 requests | 1 minute |
| Write Operations (POST/PUT/DELETE) | 50 requests | 1 minute |
| Calculations | 20 requests | 1 minute |
| PDF Generation | 10 requests | 1 minute |
| File Uploads | 5 requests | 1 minute |

### Rate Limit Exceeded Response

**Status Code:** 429 Too Many Requests

**Response Body:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 100,
      "reset_at": "2024-01-15T10:35:00Z"
    }
  }
}
```

### Best Practices

1. **Monitor Headers:** Check rate limit headers in responses
2. **Implement Backoff:** Use exponential backoff when approaching limits
3. **Cache Responses:** Cache GET responses to reduce API calls
4. **Batch Operations:** Use batch endpoints when available
5. **Optimize Requests:** Only request data you need

---

## Endpoints

### Health Check

#### GET /health

Check API health status.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "app": "Solar Calculator Pro",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### System Settings

#### GET /api/v1/system-settings

Retrieve all system settings.

**Authentication:** Required (Admin)

**Response:**
```json
{
  "general": {
    "app_name": "Solar Calculator Pro",
    "language": "de",
    "timezone": "Europe/Berlin"
  },
  "email": {
    "smtp_host": "smtp.example.com",
    "smtp_port": 587,
    "from_address": "noreply@example.com"
  },
  "backup": {
    "enabled": true,
    "frequency": "daily",
    "retention_days": 30
  }
}
```

#### PUT /api/v1/system-settings

Update system settings.

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "general": {
    "language": "en"
  }
}
```

**Response:**
```json
{
  "message": "Settings updated successfully",
  "updated_fields": ["general.language"]
}
```

---

### Database Management

#### POST /api/v1/database/backup

Create a database backup.

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "include_data": true,
  "compress": true
}
```

**Response:**
```json
{
  "backup_id": "backup_20240115_103000",
  "file_path": "/backups/backup_20240115_103000.db.gz",
  "size_bytes": 1048576,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### POST /api/v1/database/restore

Restore database from backup.

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "backup_id": "backup_20240115_103000"
}
```

**Response:**
```json
{
  "message": "Database restored successfully",
  "restored_from": "backup_20240115_103000",
  "restored_at": "2024-01-15T10:35:00Z"
}
```

---

### User Management

#### GET /api/v1/users

List all users.

**Authentication:** Required (Admin)

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `per_page` (integer, default: 20): Items per page
- `role` (string, optional): Filter by role
- `search` (string, optional): Search by name or email

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
}
```

#### POST /api/v1/users

Create a new user.

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "role": "user"
}
```

**Response:**
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /api/v1/users/{user_id}

Get user details.

**Authentication:** Required

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:00:00Z",
  "settings": {
    "language": "de",
    "theme": "light"
  }
}
```

#### PUT /api/v1/users/{user_id}

Update user information.

**Authentication:** Required (Self or Admin)

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "settings": {
    "theme": "dark"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "newemail@example.com",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### DELETE /api/v1/users/{user_id}

Delete a user.

**Authentication:** Required (Admin)

**Response:**
```json
{
  "message": "User deleted successfully",
  "deleted_id": 2
}
```

---

## Error Codes

### Authentication Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| AUTH_001 | 401 | Invalid credentials | Check username and password |
| AUTH_002 | 401 | Token expired | Refresh or obtain new token |
| AUTH_003 | 401 | Invalid token | Obtain new token |
| AUTH_004 | 403 | Insufficient permissions | Contact administrator |
| AUTH_005 | 401 | Token missing | Include Authorization header |

### Validation Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| VAL_001 | 422 | Missing required field | Include all required fields |
| VAL_002 | 422 | Invalid field format | Check field format requirements |
| VAL_003 | 422 | Value out of range | Provide value within valid range |
| VAL_004 | 422 | Invalid data type | Provide correct data type |
| VAL_005 | 422 | Field too long | Reduce field length |

### Resource Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| RES_001 | 404 | Resource not found | Check resource ID |
| RES_002 | 409 | Resource already exists | Use different identifier |
| RES_003 | 409 | Resource in use | Remove dependencies first |
| RES_004 | 410 | Resource deleted | Resource no longer available |

### Database Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| DB_001 | 500 | Database connection failed | Check database status |
| DB_002 | 500 | Query execution failed | Contact support |
| DB_003 | 409 | Constraint violation | Check data integrity |
| DB_004 | 500 | Transaction failed | Retry operation |

### File Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| FILE_001 | 400 | Invalid file type | Upload supported file type |
| FILE_002 | 413 | File too large | Reduce file size |
| FILE_003 | 400 | File corrupted | Upload valid file |
| FILE_004 | 500 | File processing failed | Try again or contact support |

### Rate Limit Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| RATE_001 | 429 | Rate limit exceeded | Wait and retry |
| RATE_002 | 429 | Too many login attempts | Wait before retrying |

### System Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| SYS_001 | 500 | Internal server error | Contact support |
| SYS_002 | 503 | Service unavailable | Try again later |
| SYS_003 | 500 | Configuration error | Contact administrator |

---

## Request/Response Examples

### Example 1: Complete Authentication Flow

```bash
# Step 1: Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@example.com",
    "password": "SecurePass123!"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Step 2: Use token for authenticated request
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Step 3: Refresh token before expiration
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Example 2: Error Handling

```bash
# Request with invalid data
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "",
    "email": "invalid-email"
  }'

# Error Response:
{
  "error": {
    "code": "VAL_001",
    "message": "Validation failed",
    "details": {
      "username": "Field is required",
      "email": "Invalid email format"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Example 3: Pagination

```bash
# Request with pagination
curl -X GET "http://localhost:8000/api/v1/users?page=2&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "users": [...],
  "pagination": {
    "page": 2,
    "per_page": 10,
    "total": 45,
    "pages": 5,
    "has_next": true,
    "has_prev": true
  }
}
```

### Example 4: Filtering and Search

```bash
# Search users by email
curl -X GET "http://localhost:8000/api/v1/users?search=admin&role=admin" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Best Practices

### 1. Always Use HTTPS in Production

```javascript
// ❌ Bad
const API_URL = 'http://api.example.com';

// ✅ Good
const API_URL = 'https://api.example.com';
```

### 2. Handle Errors Gracefully

```javascript
async function fetchData() {
  try {
    const response = await fetch('/api/v1/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API Error:', error.error.code, error.error.message);
      // Handle specific error codes
      if (error.error.code === 'AUTH_002') {
        // Token expired, refresh it
        await refreshToken();
      }
    }
    
    return await response.json();
  } catch (error) {
    console.error('Network error:', error);
    // Handle network errors
  }
}
```

### 3. Implement Token Refresh

```javascript
let token = localStorage.getItem('token');
let tokenExpiry = localStorage.getItem('tokenExpiry');

async function refreshToken() {
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  token = data.access_token;
  tokenExpiry = Date.now() + (data.expires_in * 1000);
  
  localStorage.setItem('token', token);
  localStorage.setItem('tokenExpiry', tokenExpiry);
}

// Check token expiry before each request
async function apiRequest(url, options = {}) {
  if (Date.now() >= tokenExpiry - 60000) { // Refresh 1 min before expiry
    await refreshToken();
  }
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
}
```

### 4. Use Pagination for Large Datasets

```javascript
async function fetchAllUsers() {
  let allUsers = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await fetch(`/api/v1/users?page=${page}&per_page=100`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    allUsers = [...allUsers, ...data.users];
    hasMore = data.pagination.has_next;
    page++;
  }
  
  return allUsers;
}
```

### 5. Implement Retry Logic with Exponential Backoff

```javascript
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) {
        // Rate limited, wait and retry
        const retryAfter = response.headers.get('Retry-After') || Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        continue;
      }
      
      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
}
```

### 6. Cache Responses

```javascript
const cache = new Map();

async function fetchWithCache(url, options = {}, ttl = 60000) {
  const cacheKey = `${url}_${JSON.stringify(options)}`;
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() < cached.expiry) {
    return cached.data;
  }
  
  const response = await fetch(url, options);
  const data = await response.json();
  
  cache.set(cacheKey, {
    data,
    expiry: Date.now() + ttl
  });
  
  return data;
}
```

### 7. Validate Input Before Sending

```javascript
function validateUserInput(userData) {
  const errors = {};
  
  if (!userData.username || userData.username.length < 3) {
    errors.username = 'Username must be at least 3 characters';
  }
  
  if (!userData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userData.email)) {
    errors.email = 'Invalid email format';
  }
  
  if (Object.keys(errors).length > 0) {
    throw new ValidationError(errors);
  }
}

// Use before API call
try {
  validateUserInput(userData);
  await createUser(userData);
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle validation errors locally
  }
}
```

### 8. Monitor Rate Limits

```javascript
function checkRateLimit(response) {
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');
  
  if (remaining < limit * 0.1) { // Less than 10% remaining
    console.warn(`Rate limit warning: ${remaining}/${limit} requests remaining`);
    console.warn(`Resets at: ${new Date(reset * 1000)}`);
  }
}
```

---

## Additional Resources

- **Interactive API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative API Documentation:** http://localhost:8000/redoc (ReDoc)
- **OpenAPI Specification:** http://localhost:8000/openapi.json
- **Postman Collection:** [Download](./postman_collection.json)

## Support

For API support, please contact:
- **Email:** api-support@example.com
- **Documentation:** https://docs.example.com
- **GitHub Issues:** https://github.com/example/solar-calculator-pro/issues

---

**Last Updated:** 2024-01-15  
**API Version:** 1.0.0
