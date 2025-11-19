# Authentication UI - Quick Reference

## Components Overview

### Login Page
**Location:** `src/pages/Login.tsx`

**Usage:**
```tsx
import Login from '@pages/Login';

// Automatically handles authentication and redirect
<Route path="/auth/login" element={<Login />} />
```

**Features:**
- Form validation
- Remember me checkbox
- Password visibility toggle
- Error handling
- Loading states

---

### Profile Page
**Location:** `src/pages/Profile.tsx`

**Usage:**
```tsx
import Profile from '@pages/Profile';

// Display and edit user profile
<Profile />
```

**Features:**
- Display user info
- Edit mode
- Form validation
- Save/cancel actions

---

### Password Change Form
**Location:** `src/components/PasswordChangeForm.tsx`

**Usage:**
```tsx
import { PasswordChangeForm } from '@components';

// Standalone password change form
<PasswordChangeForm />
```

**Features:**
- Current password verification
- Password strength indicator
- Confirmation matching
- Comprehensive validation

---

### Protected Route
**Location:** `src/components/ProtectedRoute.tsx`

**Usage:**
```tsx
import { ProtectedRoute } from '@components';

// Wrap routes that require authentication
<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } 
/>

// With role requirement
<Route 
  path="/admin" 
  element={
    <ProtectedRoute requiredRole="admin">
      <Admin />
    </ProtectedRoute>
  } 
/>
```

---

## Hooks

### useAuth Hook
**Location:** `src/hooks/useAuth.ts`

**Usage:**
```tsx
import { useAuth } from '@hooks/useAuth';

function MyComponent() {
  const { 
    user,              // Current user object
    isAuthenticated,   // Boolean auth status
    isLoading,         // Loading state
    error,             // Error message
    login,             // Login function
    logout,            // Logout function
    refreshUser        // Refresh user data
  } = useAuth();

  // Login
  const handleLogin = async () => {
    const success = await login({
      username: 'user',
      password: 'pass'
    });
    if (success) {
      // Handle success
    }
  };

  // Logout
  const handleLogout = async () => {
    await logout();
  };

  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user?.username}!</p>
      ) : (
        <p>Please log in</p>
      )}
    </div>
  );
}
```

---

## Services

### Auth Service
**Location:** `src/services/auth.ts`

**Methods:**
```typescript
import { authService } from '@services/auth';

// Login
await authService.login({ username, password });

// Logout
await authService.logout();

// Get current user
const user = await authService.getCurrentUser();

// Refresh token
await authService.refreshToken();

// Change password
await authService.changePassword(currentPassword, newPassword);

// Update profile
const updatedUser = await authService.updateProfile({ email: 'new@email.com' });

// Check authentication
const isAuth = authService.isAuthenticated();

// Get token
const token = authService.getToken();
```

---

## State Management

### Auth Store
**Location:** `src/store/authStore.ts`

**Usage:**
```tsx
import { useAuthStore } from '@store/authStore';

function MyComponent() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const setUser = useAuthStore((state) => state.setUser);
  const logout = useAuthStore((state) => state.logout);

  return (
    <div>
      {isAuthenticated && <p>{user?.username}</p>}
    </div>
  );
}
```

---

## Validation Rules

### Username
- Required
- Minimum 3 characters
- Trimmed whitespace

### Email
- Required
- Valid email format: `user@domain.com`

### Password (Login)
- Required
- Minimum 6 characters

### Password (Change)
- Required
- Minimum 8 characters
- Must include:
  - Lowercase letters
  - Uppercase letters
  - Numbers
  - Special characters
- Strength score ≥ 3 (out of 5)
- Must differ from current password

### Password Confirmation
- Must match new password

---

## API Endpoints

### Authentication Endpoints

```typescript
// Login
POST /api/v1/auth/login
Body: { username: string, password: string }
Response: { access_token: string, token_type: string, expires_in: number }

// Logout
POST /api/v1/auth/logout
Response: void

// Get current user
GET /api/v1/auth/me
Response: { id: number, username: string, email: string, role: string, created_at: string }

// Refresh token
POST /api/v1/auth/refresh
Response: { access_token: string, token_type: string, expires_in: number }

// Change password
POST /api/v1/auth/change-password
Body: { current_password: string, new_password: string }
Response: void

// Update profile
PUT /api/v1/auth/profile
Body: { username?: string, email?: string }
Response: { id: number, username: string, email: string, role: string, created_at: string }
```

---

## Common Patterns

### Login Flow
```tsx
import { useAuth } from '@hooks/useAuth';
import { useNavigate } from 'react-router-dom';

function LoginComponent() {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (credentials) => {
    const success = await login(credentials);
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
      {error && <p>{error}</p>}
    </form>
  );
}
```

### Logout Flow
```tsx
import { useAuth } from '@hooks/useAuth';

function LogoutButton() {
  const { logout } = useAuth();

  return (
    <button onClick={logout}>
      Logout
    </button>
  );
}
```

### Protected Content
```tsx
import { useAuth } from '@hooks/useAuth';

function ProtectedContent() {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <p>Please log in to view this content</p>;
  }

  return (
    <div>
      <h1>Welcome, {user?.username}!</h1>
      {/* Protected content */}
    </div>
  );
}
```

### Role-Based Access
```tsx
import { useAuth } from '@hooks/useAuth';

function AdminPanel() {
  const { user } = useAuth();

  if (user?.role !== 'admin') {
    return <p>Access denied</p>;
  }

  return (
    <div>
      {/* Admin content */}
    </div>
  );
}
```

---

## Styling

### CSS Variables
```css
--primary-color          /* Primary brand color */
--text-color            /* Main text color */
--text-color-secondary  /* Secondary text color */
--surface-card          /* Card background */
--surface-100           /* Light surface */
--surface-300           /* Border color */
--red-500              /* Error color */
```

### Custom Classes
```css
.login-container        /* Login page container */
.login-card            /* Login card */
.profile-container     /* Profile page container */
.profile-card          /* Profile card */
.password-change-card  /* Password form card */
.p-field               /* Form field wrapper */
.p-label               /* Form label */
.p-error               /* Error message */
.p-invalid             /* Invalid input */
```

---

## Error Handling

### Display Errors
```tsx
import { Message } from 'primereact/message';

function MyForm() {
  const [error, setError] = useState<string | null>(null);

  return (
    <div>
      {error && (
        <Message severity="error" text={error} />
      )}
      {/* Form content */}
    </div>
  );
}
```

### Field Errors
```tsx
function MyInput() {
  const [error, setError] = useState<string | undefined>();
  const [touched, setTouched] = useState(false);

  return (
    <div className="p-field">
      <label>Username</label>
      <InputText
        className={error && touched ? 'p-invalid' : ''}
        onBlur={() => setTouched(true)}
      />
      {error && touched && (
        <small className="p-error">{error}</small>
      )}
    </div>
  );
}
```

---

## Remember Me Feature

### Implementation
```tsx
// Save username
if (rememberMe) {
  localStorage.setItem('remembered_username', username);
} else {
  localStorage.removeItem('remembered_username');
}

// Load username
useEffect(() => {
  const remembered = localStorage.getItem('remembered_username');
  if (remembered) {
    setUsername(remembered);
    setRememberMe(true);
  }
}, []);
```

---

## Password Strength Indicator

### Usage
```tsx
import { useState } from 'react';

function PasswordInput() {
  const [password, setPassword] = useState('');

  const checkStrength = (pwd: string) => {
    let score = 0;
    if (pwd.length >= 8) score++;
    if (/[a-z]/.test(pwd)) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^a-zA-Z0-9]/.test(pwd)) score++;
    return score;
  };

  const strength = checkStrength(password);
  const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];

  return (
    <div>
      <Password value={password} onChange={(e) => setPassword(e.target.value)} />
      <div className="strength-bar">
        <div style={{ width: `${(strength / 5) * 100}%` }} />
      </div>
      <small>{labels[strength]}</small>
    </div>
  );
}
```

---

## Troubleshooting

### Issue: Login not working
**Check:**
1. Backend API is running
2. Correct API endpoint URL
3. Network tab for errors
4. Token storage in localStorage

### Issue: Protected routes not working
**Check:**
1. ProtectedRoute wrapper is used
2. Auth state is initialized
3. Token is valid
4. User data is loaded

### Issue: Remember me not working
**Check:**
1. localStorage is enabled
2. Username is being saved
3. useEffect is loading data
4. Checkbox state is correct

### Issue: Password strength not showing
**Check:**
1. Password value is not empty
2. Strength calculation is correct
3. CSS for strength bar is loaded
4. Component is rendering indicator

---

## Best Practices

1. **Always validate on both client and server**
2. **Use HTTPS in production**
3. **Never log sensitive data**
4. **Clear tokens on logout**
5. **Handle token expiration**
6. **Provide clear error messages**
7. **Use loading states**
8. **Implement rate limiting**
9. **Test authentication flows**
10. **Keep dependencies updated**
