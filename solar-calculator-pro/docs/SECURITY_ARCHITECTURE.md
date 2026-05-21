# Security Architecture

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Security](#data-security)
4. [Network Security](#network-security)
5. [Application Security](#application-security)
6. [Electron Security](#electron-security)
7. [Security Best Practices](#security-best-practices)

## Overview

Solar Calculator Pro implements multiple layers of security to protect user data, prevent unauthorized access, and ensure safe operation.

### Security Principles

- **Defense in Depth**: Multiple security layers
- **Least Privilege**: Minimal permissions required
- **Secure by Default**: Security enabled out of the box
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: All inputs validated and sanitized
- **Audit Logging**: Security events logged

## Authentication & Authorization

### Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│              Authentication Process                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: User Login                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Frontend                                         │  │
│  │  • User enters credentials                        │  │
│  │  • Password hashed client-side (optional)        │  │
│  │  • POST /api/v1/auth/login                       │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                 │
│                        ▼                                 │
│  Step 2: Credential Verification                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Backend                                          │  │
│  │  • Retrieve user from database                    │  │
│  │  • Verify password with bcrypt                    │  │
│  │  • Check account status (active/locked)          │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                 │
│                        ▼                                 │
│  Step 3: Token Generation                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Backend                                          │  │
│  │  • Generate JWT access token (15 min)            │  │
│  │  • Generate refresh token (7 days)               │  │
│  │  • Store refresh token in database               │  │
│  │  • Return tokens to client                       │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                 │
│                        ▼                                 │
│  Step 4: Token Storage                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Frontend                                         │  │
│  │  • Store access token in memory                  │  │
│  │  • Store refresh token in httpOnly cookie        │  │
│  │  • Update auth state in Zustand                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### JWT Token Structure

```python
# backend/core/security.py

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### Authorization Model

```
┌─────────────────────────────────────────────────────────┐
│              Role-Based Access Control                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Roles                                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Admin: Full system access                      │  │
│  │  • Manager: User management, reports              │  │
│  │  • User: Standard features                        │  │
│  │  • Guest: Read-only access                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Permissions                                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • projects:read                                  │  │
│  │  • projects:write                                 │  │
│  │  • projects:delete                                │  │
│  │  • users:manage                                   │  │
│  │  • settings:modify                                │  │
│  │  • reports:generate                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Permission Check                                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  @require_permission("projects:write")            │  │
│  │  async def create_project(...)                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Data Security

### Encryption at Rest

```
┌─────────────────────────────────────────────────────────┐
│              Data Encryption Strategy                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Database Encryption                                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • SQLite encryption with SQLCipher               │  │
│  │  • AES-256 encryption                             │  │
│  │  • Key derived from master password              │  │
│  │  • Transparent encryption/decryption             │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Sensitive Field Encryption                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Customer data encrypted                        │  │
│  │  • Financial information encrypted                │  │
│  │  • API keys encrypted                             │  │
│  │  • Fernet symmetric encryption                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  File Encryption                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • PDF files encrypted                            │  │
│  │  • Backup files encrypted                         │  │
│  │  • Export files encrypted                         │  │
│  │  • AES-256-GCM encryption                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Password Security

```python
# Password Requirements
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not in common password list
- Not similar to username

# Password Storage
- Hashed with bcrypt (cost factor 12)
- Salted automatically by bcrypt
- Never stored in plain text
- Never logged or transmitted in plain text

# Password Reset
- Secure token generation
- Token expires after 1 hour
- Token single-use only
- Email verification required
```

## Network Security

### HTTPS/TLS

```
┌─────────────────────────────────────────────────────────┐
│              Network Security Layers                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Local Communication (Electron)                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Frontend ◄──────HTTPS──────► Backend            │  │
│  │  (Port 3000)    (localhost)   (Port 8000)        │  │
│  │                                                   │  │
│  │  • Self-signed certificate for localhost         │  │
│  │  • TLS 1.3                                        │  │
│  │  • Certificate pinning                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  External Communication                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Application ◄────HTTPS────► External APIs       │  │
│  │                                                   │  │
│  │  • Certificate validation                         │  │
│  │  • TLS 1.2 minimum                               │  │
│  │  • Strong cipher suites only                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### API Security

```python
# backend/middleware/security_headers.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
```

### Rate Limiting

```python
# backend/middleware/rate_limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to endpoints
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, credentials: LoginRequest):
    pass

@app.post("/api/v1/solar/calculate")
@limiter.limit("100/hour")  # 100 calculations per hour
async def calculate(request: Request, data: CalculationRequest):
    pass
```

## Application Security

### Input Validation

```python
# backend/models/schemas.py

from pydantic import BaseModel, Field, validator
import re

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    customer_email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    roof_area: float = Field(..., gt=0, lt=10000)
    
    @validator('name')
    def validate_name(cls, v):
        # Prevent XSS
        if re.search(r'[<>]', v):
            raise ValueError('Invalid characters in name')
        return v
    
    @validator('customer_email')
    def validate_email(cls, v):
        # Additional email validation
        if len(v) > 254:
            raise ValueError('Email too long')
        return v.lower()
```

### SQL Injection Prevention

```python
# Using SQLAlchemy ORM (parameterized queries)

# SAFE - Parameterized query
users = session.query(User).filter(User.username == username).all()

# SAFE - Using bound parameters
stmt = select(User).where(User.username == bindparam('username'))
result = session.execute(stmt, {'username': username})

# NEVER DO THIS - String concatenation
# query = f"SELECT * FROM users WHERE username = '{username}'"  # UNSAFE!
```

### XSS Prevention

```typescript
// frontend/src/utils/sanitizer.ts

import DOMPurify from 'dompurify';

export function sanitizeHTML(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href']
  });
}

// React automatically escapes content
// Only use dangerouslySetInnerHTML with sanitized content
<div dangerouslySetInnerHTML={{ __html: sanitizeHTML(userContent) }} />
```

### CSRF Protection

```python
# backend/middleware/csrf_protection.py

from fastapi import Request, HTTPException
import secrets

class CSRFProtection:
    def __init__(self):
        self.tokens = {}  # In production, use Redis
    
    def generate_token(self, session_id: str) -> str:
        token = secrets.token_urlsafe(32)
        self.tokens[session_id] = token
        return token
    
    def validate_token(self, session_id: str, token: str) -> bool:
        expected = self.tokens.get(session_id)
        if not expected or expected != token:
            return False
        del self.tokens[session_id]  # Single use
        return True

# Apply to state-changing endpoints
@app.post("/api/v1/projects")
async def create_project(
    request: Request,
    csrf_token: str = Header(...),
    data: ProjectCreate
):
    if not csrf.validate_token(request.session_id, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    # Process request
```

## Electron Security

### Context Isolation

```javascript
// electron/main.js

const mainWindow = new BrowserWindow({
  width: 1200,
  height: 800,
  webPreferences: {
    // Security settings
    contextIsolation: true,        // Isolate renderer context
    nodeIntegration: false,         // Disable Node.js in renderer
    nodeIntegrationInWorker: false, // Disable in web workers
    nodeIntegrationInSubFrames: false, // Disable in iframes
    sandbox: true,                  // Enable sandbox
    webSecurity: true,              // Enable web security
    allowRunningInsecureContent: false,
    experimentalFeatures: false,
    enableBlinkFeatures: '',
    disableBlinkFeatures: '',
    preload: path.join(__dirname, 'preload.js')
  }
});
```

### Secure IPC

```javascript
// electron/preload.js

const { contextBridge, ipcRenderer } = require('electron');

// Whitelist of allowed channels
const validChannels = [
  'file:open',
  'file:save',
  'backend:getUrl',
  'window:minimize',
  'window:maximize',
  'window:close'
];

contextBridge.exposeInMainWorld('electronAPI', {
  // Only expose specific, validated functions
  selectFile: () => ipcRenderer.invoke('file:open'),
  saveFile: (data) => {
    // Validate data before sending
    if (typeof data !== 'object') {
      throw new Error('Invalid data type');
    }
    return ipcRenderer.invoke('file:save', data);
  },
  
  // Never expose these:
  // - require
  // - process
  // - child_process
  // - fs
});
```

### Content Security Policy

```javascript
// electron/main.js

session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self' http://localhost:8000 ws://localhost:8000",
        "frame-src 'none'",
        "object-src 'none'"
      ].join('; ')
    }
  });
});
```

## Security Best Practices

### Secure Configuration

```python
# backend/config.py

from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # Database
    DATABASE_URL: str
    DATABASE_ENCRYPTION_KEY: str
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
```

### Audit Logging

```python
# backend/core/audit_logger.py

import logging
from datetime import datetime
from typing import Optional

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[int],
        action: str,
        resource: str,
        result: str,
        ip_address: str,
        details: dict = None
    ):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'result': result,
            'ip_address': ip_address,
            'details': details or {}
        }
        self.logger.info(log_entry)

# Usage
audit = AuditLogger()
audit.log_event(
    event_type='authentication',
    user_id=user.id,
    action='login',
    resource='auth',
    result='success',
    ip_address=request.client.host
)
```

### Security Checklist

#### Authentication & Authorization
- [ ] Strong password requirements enforced
- [ ] Passwords hashed with bcrypt
- [ ] JWT tokens with short expiration
- [ ] Refresh token rotation
- [ ] Role-based access control implemented
- [ ] Session management secure

#### Data Protection
- [ ] Database encryption enabled
- [ ] Sensitive fields encrypted
- [ ] Secure key management
- [ ] Data backup encrypted
- [ ] PII handling compliant

#### Network Security
- [ ] HTTPS/TLS enforced
- [ ] Certificate validation
- [ ] Security headers set
- [ ] CORS configured properly
- [ ] Rate limiting implemented

#### Application Security
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Error messages don't leak info

#### Electron Security
- [ ] Context isolation enabled
- [ ] Node integration disabled
- [ ] Sandbox enabled
- [ ] Secure IPC channels
- [ ] CSP configured

#### Monitoring & Logging
- [ ] Security events logged
- [ ] Failed login attempts tracked
- [ ] Audit trail maintained
- [ ] Error monitoring active
- [ ] Security alerts configured

## Summary

The security architecture provides:

- **Multi-Layer Defense**: Security at every level
- **Authentication**: Secure JWT-based authentication
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: All inputs validated and sanitized
- **Electron Security**: Context isolation and secure IPC
- **Audit Logging**: Complete audit trail
- **Best Practices**: Industry-standard security measures
