# Authentication Guide

## Overview

The Solar Calculator Pro API uses JWT (JSON Web Token) based authentication to secure endpoints and manage user sessions. This guide covers everything you need to know about authenticating with the API.

## Table of Contents

1. [Authentication Flow](#authentication-flow)
2. [Obtaining Tokens](#obtaining-tokens)
3. [Using Tokens](#using-tokens)
4. [Token Refresh](#token-refresh)
5. [Token Expiration](#token-expiration)
6. [Security Best Practices](#security-best-practices)
7. [Common Issues](#common-issues)

---

## Authentication Flow

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │  Server │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  1. POST /auth/login                        │
     │  { username, password }                     │
     ├────────────────────────────────────────────>│
     │                                              │
     │  2. Validate credentials                    │
     │                                              │
     │  3. Generate JWT token                      │
     │                                              │
     │  4. Return token                            │
     │  { access_token, expires_in }               │
     │<────────────────────────────────────────────┤
     │                                              │
     │  5. Store token securely                    │
     │                                              │
     │  6. Include token in requests               │
     │  Authorization: Bearer <token>              │
     ├────────────────────────────────────────────>│
     │                                              │
     │  7. Validate token                          │
     │                                              │
     │  8. Process request                         │
     │                                              │
     │  9. Return response                         │
     │<────────────────────────────────────────────┤
     │                                              │
```

---

## Obtaining Tokens

### Login Endpoint

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```http
POST /api/v1/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjQyMjQ4MDAwfQ.signature",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTH_001",
    "message": "Invalid credentials",
    "details": {
      "reason": "Username or password is incorrect"
    }
  }
}
```

### Implementation Examples

#### JavaScript/TypeScript
```javascript
async function login(username, password) {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }

  const data = await response.json();
  
  // Store token securely
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('token_expiry', Date.now() + (data.expires_in * 1000));
  
  return data;
}
```

#### Python
```python
import requests
from datetime import datetime, timedelta

def login(username: str, password: str) -> dict:
    response = requests.post(
        'http://localhost:8000/api/v1/auth/login',
        json={'username': username, 'password': password}
    )
    
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.json()['error']['message']}")
    
    data = response.json()
    
    # Store token (example using file)
    with open('.token', 'w') as f:
        f.write(data['access_token'])
    
    return data
```

#### curl
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

---

## Using Tokens

### Authorization Header

Include the token in the `Authorization` header with the `Bearer` scheme:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Implementation Examples

#### JavaScript/TypeScript
```javascript
async function makeAuthenticatedRequest(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No authentication token found');
  }
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 401) {
    // Token invalid or expired
    localStorage.removeItem('access_token');
    throw new Error('Authentication required');
  }
  
  return response;
}

// Usage
const response = await makeAuthenticatedRequest('http://localhost:8000/api/v1/users');
const users = await response.json();
```

#### Python
```python
import requests

def make_authenticated_request(url: str, method: str = 'GET', **kwargs) -> requests.Response:
    with open('.token', 'r') as f:
        token = f.read().strip()
    
    headers = kwargs.get('headers', {})
    headers['Authorization'] = f'Bearer {token}'
    kwargs['headers'] = headers
    
    response = requests.request(method, url, **kwargs)
    
    if response.status_code == 401:
        raise Exception('Authentication required')
    
    return response

# Usage
response = make_authenticated_request('http://localhost:8000/api/v1/users')
users = response.json()
```

#### curl
```bash
TOKEN="your_token_here"

curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/users
```

---

## Token Refresh

### Why Refresh Tokens?

- Tokens expire after a set period (default: 1 hour)
- Refreshing extends the session without re-entering credentials
- Improves security by limiting token lifetime

### Refresh Endpoint

**Endpoint:** `POST /api/v1/auth/refresh`

**Request:**
```http
POST /api/v1/auth/refresh HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new_token...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Implementation Examples

#### JavaScript/TypeScript with Auto-Refresh
```javascript
class AuthManager {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.tokenExpiry = parseInt(localStorage.getItem('token_expiry') || '0');
    this.refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiry
  }

  async refreshToken() {
    const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    this.token = data.access_token;
    this.tokenExpiry = Date.now() + (data.expires_in * 1000);

    localStorage.setItem('access_token', this.token);
    localStorage.setItem('token_expiry', this.tokenExpiry.toString());

    return data;
  }

  async ensureValidToken() {
    const timeUntilExpiry = this.tokenExpiry - Date.now();

    if (timeUntilExpiry < this.refreshThreshold) {
      await this.refreshToken();
    }
  }

  async makeRequest(url, options = {}) {
    await this.ensureValidToken();

    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.token}`
      }
    });
  }
}

// Usage
const auth = new AuthManager();
const response = await auth.makeRequest('http://localhost:8000/api/v1/users');
```

#### Python with Auto-Refresh
```python
import requests
from datetime import datetime, timedelta
import time

class AuthManager:
    def __init__(self):
        self.token = None
        self.token_expiry = None
        self.refresh_threshold = timedelta(minutes=5)
        self.load_token()
    
    def load_token(self):
        try:
            with open('.token', 'r') as f:
                self.token = f.read().strip()
            with open('.token_expiry', 'r') as f:
                self.token_expiry = datetime.fromisoformat(f.read().strip())
        except FileNotFoundError:
            pass
    
    def save_token(self, token: str, expires_in: int):
        self.token = token
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
        
        with open('.token', 'w') as f:
            f.write(token)
        with open('.token_expiry', 'w') as f:
            f.write(self.token_expiry.isoformat())
    
    def refresh_token(self):
        response = requests.post(
            'http://localhost:8000/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if response.status_code != 200:
            raise Exception('Token refresh failed')
        
        data = response.json()
        self.save_token(data['access_token'], data['expires_in'])
    
    def ensure_valid_token(self):
        if not self.token or not self.token_expiry:
            raise Exception('No token available')
        
        time_until_expiry = self.token_expiry - datetime.now()
        
        if time_until_expiry < self.refresh_threshold:
            self.refresh_token()
    
    def make_request(self, url: str, method: str = 'GET', **kwargs):
        self.ensure_valid_token()
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        return requests.request(method, url, **kwargs)

# Usage
auth = AuthManager()
response = auth.make_request('http://localhost:8000/api/v1/users')
```

---

## Token Expiration

### Default Expiration Times

| Token Type | Expiration |
|------------|------------|
| Access Token | 1 hour (3600 seconds) |
| Refresh Window | 5 minutes before expiry |

### Handling Expired Tokens

When a token expires, the API returns a 401 Unauthorized response:

```json
{
  "error": {
    "code": "AUTH_002",
    "message": "Token expired",
    "details": {
      "expired_at": "2024-01-15T11:30:00Z"
    }
  }
}
```

### Best Practices

1. **Proactive Refresh:** Refresh tokens before they expire
2. **Graceful Degradation:** Handle expired tokens gracefully
3. **User Experience:** Don't interrupt user actions
4. **Logout on Failure:** If refresh fails, log user out

```javascript
async function handleApiCall(apiFunction) {
  try {
    return await apiFunction();
  } catch (error) {
    if (error.code === 'AUTH_002') {
      // Token expired, try to refresh
      try {
        await refreshToken();
        return await apiFunction(); // Retry
      } catch (refreshError) {
        // Refresh failed, logout user
        logout();
        throw new Error('Session expired. Please login again.');
      }
    }
    throw error;
  }
}
```

---

## Security Best Practices

### 1. Secure Token Storage

#### ✅ Good Practices

**Browser (Frontend):**
```javascript
// Use httpOnly cookies (set by server)
// Or use sessionStorage for single-tab sessions
sessionStorage.setItem('access_token', token);

// For multi-tab, use localStorage with encryption
import CryptoJS from 'crypto-js';

function storeToken(token) {
  const encrypted = CryptoJS.AES.encrypt(token, SECRET_KEY).toString();
  localStorage.setItem('access_token', encrypted);
}

function getToken() {
  const encrypted = localStorage.getItem('access_token');
  if (!encrypted) return null;
  
  const decrypted = CryptoJS.AES.decrypt(encrypted, SECRET_KEY);
  return decrypted.toString(CryptoJS.enc.Utf8);
}
```

**Electron (Desktop):**
```javascript
// Use electron-store with encryption
import Store from 'electron-store';

const store = new Store({
  encryptionKey: 'your-encryption-key',
  name: 'auth'
});

store.set('access_token', token);
const token = store.get('access_token');
```

**Mobile:**
```javascript
// Use secure storage libraries
// iOS: Keychain
// Android: Keystore
```

#### ❌ Bad Practices

```javascript
// DON'T store in plain localStorage without encryption
localStorage.setItem('token', token); // Vulnerable to XSS

// DON'T store in cookies without httpOnly flag
document.cookie = `token=${token}`; // Vulnerable to XSS

// DON'T store in URL or query parameters
window.location.href = `/dashboard?token=${token}`; // Exposed in logs

// DON'T log tokens
console.log('Token:', token); // Exposed in console
```

### 2. HTTPS Only

```javascript
// ✅ Always use HTTPS in production
const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://api.example.com'
  : 'http://localhost:8000';

// ❌ Never use HTTP in production
const API_URL = 'http://api.example.com'; // Insecure!
```

### 3. Token Validation

```javascript
// Validate token format before using
function isValidToken(token) {
  if (!token) return false;
  
  // JWT format: header.payload.signature
  const parts = token.split('.');
  if (parts.length !== 3) return false;
  
  try {
    // Decode payload (don't verify signature client-side)
    const payload = JSON.parse(atob(parts[1]));
    
    // Check expiration
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      return false;
    }
    
    return true;
  } catch {
    return false;
  }
}
```

### 4. Logout Properly

```javascript
async function logout() {
  try {
    // Call logout endpoint if available
    await fetch('http://localhost:8000/api/v1/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Always clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_expiry');
    sessionStorage.clear();
    
    // Redirect to login
    window.location.href = '/login';
  }
}
```

### 5. Handle Token in Requests

```javascript
// Use interceptors to add token automatically
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      try {
        await refreshToken();
        // Retry original request
        return api.request(error.config);
      } catch {
        logout();
      }
    }
    return Promise.reject(error);
  }
);
```

---

## Common Issues

### Issue 1: "Token expired" Error

**Cause:** Token has exceeded its expiration time

**Solution:**
```javascript
// Implement automatic token refresh
async function ensureValidToken() {
  const expiry = parseInt(localStorage.getItem('token_expiry'));
  const now = Date.now();
  
  if (now >= expiry - (5 * 60 * 1000)) { // 5 min before expiry
    await refreshToken();
  }
}
```

### Issue 2: "Invalid token" Error

**Cause:** Token is malformed or tampered with

**Solution:**
```javascript
// Validate token format
function validateTokenFormat(token) {
  const parts = token.split('.');
  return parts.length === 3;
}

// If invalid, clear and re-login
if (!validateTokenFormat(token)) {
  localStorage.removeItem('access_token');
  redirectToLogin();
}
```

### Issue 3: Token Not Included in Request

**Cause:** Authorization header not set

**Solution:**
```javascript
// Always include Authorization header
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### Issue 4: CORS Error with Authorization Header

**Cause:** Server not configured to accept Authorization header

**Solution (Backend):**
```python
# In FastAPI main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Includes Authorization
)
```

### Issue 5: Token Lost on Page Refresh

**Cause:** Using sessionStorage or not persisting token

**Solution:**
```javascript
// Use localStorage for persistence
localStorage.setItem('access_token', token);

// Or use cookies with appropriate flags
document.cookie = `token=${token}; Secure; HttpOnly; SameSite=Strict`;
```

---

## Testing Authentication

### Manual Testing with curl

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.access_token')

# 2. Use token
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/users

# 3. Refresh token
NEW_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.access_token')
```

### Automated Testing

```javascript
// Jest test example
describe('Authentication', () => {
  let token;

  test('should login successfully', async () => {
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'test@example.com',
        password: 'password'
      })
    });

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.access_token).toBeDefined();
    token = data.access_token;
  });

  test('should access protected endpoint', async () => {
    const response = await fetch('http://localhost:8000/api/v1/users', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    expect(response.status).toBe(200);
  });

  test('should refresh token', async () => {
    const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.access_token).toBeDefined();
  });
});
```

---

## Additional Resources

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [API Documentation](./API_DOCUMENTATION.md)
- [Quick Reference](./API_QUICK_REFERENCE.md)

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0
