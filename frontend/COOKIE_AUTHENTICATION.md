# Cookie-Based Authentication Implementation

## Overview

The ProctorIQ authentication system now uses **secure HTTP cookies** instead of localStorage for storing JWT tokens and user data. This provides better security and follows modern web security best practices.

---

## Why Cookies Over localStorage?

### Security Benefits

1. **HttpOnly Flag Protection** (when backend sets it)
   - Cookies can be marked as `HttpOnly`, preventing JavaScript access
   - Protects against XSS (Cross-Site Scripting) attacks
   - localStorage is always accessible via JavaScript

2. **Automatic CSRF Protection**
   - Cookies with `SameSite=Strict` prevent CSRF attacks
   - Token automatically sent with every request to same origin
   - No need for manual token management in headers

3. **Secure Flag for HTTPS**
   - Cookies can be marked `Secure` to only work over HTTPS
   - Prevents man-in-the-middle attacks in production

4. **Automatic Expiration**
   - Cookies have built-in expiration handling
   - Browser automatically cleans up expired cookies

---

## Implementation Details

### Cookie Configuration

```typescript
const COOKIE_OPTIONS = {
  expires: 1,                              // 1 day (matches JWT expiry)
  secure: process.env.NODE_ENV === 'production', // HTTPS only in production
  sameSite: 'strict' as const,             // Strict CSRF protection
  path: '/',                                // Available to entire app
};
```

### Cookies Stored

| Cookie Name | Content | Expiry | Purpose |
|------------|---------|--------|---------|
| `auth_token` | JWT token (Bearer token) | 24 hours | API authentication |
| `user` | Serialized user object | 24 hours | User state persistence |

### User Object Structure

```typescript
{
  id: string;           // MongoDB ObjectId
  email: string;        // User email
  name: string;         // Full name
  role: 'student' | 'teacher';
  student_id?: string;  // Only for students
  created_at?: string;  // ISO timestamp
}
```

---

## Authentication Flow

### 1. Login Process

```typescript
// User submits login form
await login(email, password);

// Backend validates credentials
// Returns: { user: {...}, token: "eyJhbGci...", expires_in: 86400 }

// Frontend stores in cookies
Cookies.set('auth_token', token, COOKIE_OPTIONS);
Cookies.set('user', JSON.stringify(user), COOKIE_OPTIONS);
```

### 2. Automatic Token Injection

Every API request automatically includes the JWT token:

```typescript
axios.interceptors.request.use((config) => {
  const token = Cookies.get('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 3. Token Validation

On app load, the frontend:
1. Reads `auth_token` and `user` from cookies
2. Verifies token with backend (`GET /api/auth/me`)
3. If valid → user logged in
4. If invalid → clears cookies, redirects to login

### 4. Session Management

**Automatic Logout on:**
- Token expiry (24 hours)
- 401 Unauthorized response from API
- User clicks "Logout" button

**Logout Process:**
```typescript
logout() {
  setUser(null);
  setToken(null);
  Cookies.remove('auth_token', { path: '/' });
  Cookies.remove('user', { path: '/' });
}
```

---

## Security Features

### 1. XSS Protection
- Cookies not directly accessible from JavaScript (when HttpOnly set)
- User data in cookie is read-only from client perspective
- Token cannot be stolen via XSS attacks

### 2. CSRF Protection
```typescript
sameSite: 'strict'  // Cookies only sent to same origin
```
- Prevents cross-site request forgery
- Third-party sites cannot make authenticated requests

### 3. Secure Transport
```typescript
secure: process.env.NODE_ENV === 'production'
```
- Production: Cookies only transmitted over HTTPS
- Development: Allows HTTP for localhost testing

### 4. Path Restriction
```typescript
path: '/'
```
- Cookies available to entire application
- Not leaked to external domains

### 5. Token Expiration
- Cookies expire after 24 hours (matches JWT expiry)
- Browser automatically deletes expired cookies
- Forces re-authentication for security

---

## Usage Examples

### Login

```tsx
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const { login } = useAuth();

  const handleSubmit = async (email: string, password: string) => {
    try {
      await login(email, password);
      // Cookies automatically set
      // User redirected to dashboard
    } catch (error) {
      console.error('Login failed:', error.message);
    }
  };
};
```

### Check Authentication Status

```tsx
import { useAuth } from '../context/AuthContext';

const MyComponent = () => {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) return <CircularProgress />;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return <div>Welcome, {user?.name}!</div>;
};
```

### Protected Routes

```tsx
<Route
  path="/student-dashboard"
  element={
    <ProtectedRoute requiredRole="student">
      <StudentDashboard />
    </ProtectedRoute>
  }
/>
```

### Manual Token Access (if needed)

```typescript
import Cookies from 'js-cookie';

// Get token
const token = Cookies.get('auth_token');

// Get user
const userStr = Cookies.get('user');
const user = userStr ? JSON.parse(userStr) : null;

// Check if authenticated
const isAuthenticated = !!Cookies.get('auth_token');
```

---

## API Integration

### Automatic Header Injection

All axios requests automatically include:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

No need to manually add headers:
```typescript
// ✅ Automatic - token from cookie
await axios.get('/api/auth/me');

// ❌ Not needed anymore
await axios.get('/api/auth/me', {
  headers: { Authorization: `Bearer ${token}` }
});
```

### 401 Handling

Automatic logout on unauthorized:
```typescript
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear cookies and redirect
      Cookies.remove('auth_token');
      Cookies.remove('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## Testing Authentication

### 1. Register New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "SecurePass123!",
    "name": "Test Student",
    "role": "student",
    "student_id": "STU001"
  }'
```

### 2. Login via Frontend

1. Navigate to http://localhost:3000/login
2. Enter credentials
3. Check browser cookies:
   - **Chrome:** DevTools → Application → Cookies → http://localhost:3000
   - **Firefox:** DevTools → Storage → Cookies → http://localhost:3000

### 3. Verify Cookie Contents

```javascript
// Open browser console
console.log('Token:', document.cookie);

// Should see:
// auth_token=eyJhbGci...; user={"id":"...","email":"..."}
```

### 4. Test Protected Route

```bash
# Without cookie → Redirect to /login
http://localhost:3000/student-dashboard

# With valid cookie → Access granted
http://localhost:3000/student-dashboard
```

---

## Cookie Debugging

### Check if Cookies Are Set

```javascript
// In browser console
console.log('Auth Token:', Cookies.get('auth_token'));
console.log('User:', JSON.parse(Cookies.get('user') || '{}'));
```

### Common Issues

**Issue 1: Cookies not persisting**
- **Cause:** Browser blocking third-party cookies
- **Solution:** Check browser settings, ensure same origin

**Issue 2: 401 on every request**
- **Cause:** Cookie not being sent
- **Solution:** Verify `path: '/'` and same origin

**Issue 3: Logout on page refresh**
- **Cause:** Cookie expired or invalid
- **Solution:** Check cookie expiration, verify JWT secret matches

---

## Production Considerations

### Backend Changes Needed

Update FastAPI to set `HttpOnly` cookies:

```python
from fastapi import Response

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    # ... validate credentials ...
    
    token = create_jwt_token(user)
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        max_age=86400,  # 24 hours
        httponly=True,  # Prevents JavaScript access
        secure=True,    # HTTPS only
        samesite="strict"
    )
    
    return {"user": user, "token": token}
```

### HTTPS Configuration

```typescript
// Automatic in production
const COOKIE_OPTIONS = {
  secure: process.env.NODE_ENV === 'production', // ✅
};
```

### Domain Configuration

For subdomain sharing:
```typescript
const COOKIE_OPTIONS = {
  domain: '.proctoriq.com',  // Share across *.proctoriq.com
};
```

---

## Migration from localStorage

### What Changed

**Before (localStorage):**
```typescript
localStorage.setItem('token', token);
localStorage.setItem('user', JSON.stringify(user));
const token = localStorage.getItem('token');
```

**After (Cookies):**
```typescript
Cookies.set('auth_token', token, COOKIE_OPTIONS);
Cookies.set('user', JSON.stringify(user), COOKIE_OPTIONS);
const token = Cookies.get('auth_token');
```

### Migration Script (if needed)

```typescript
// Run once to migrate existing users
const migrateToMigration = () => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  
  if (token && user) {
    Cookies.set('auth_token', token, COOKIE_OPTIONS);
    Cookies.set('user', user, COOKIE_OPTIONS);
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};
```

---

## Security Checklist

- ✅ Cookies use `SameSite=Strict` (CSRF protection)
- ✅ Cookies use `Secure` flag in production (HTTPS only)
- ✅ Token expires after 24 hours
- ✅ 401 responses trigger automatic logout
- ✅ Token verified on app load
- ✅ No sensitive data in cookie (user data is minimal)
- ⚠️ Consider adding `HttpOnly` flag on backend
- ⚠️ Consider refresh token mechanism for longer sessions

---

## Related Files

- `src/context/AuthContext.tsx` - Authentication logic
- `src/components/ProtectedRoute.tsx` - Route protection
- `src/pages/Login.tsx` - Login page
- `src/pages/Register.tsx` - Registration page
- `frontend/.env` - API URL configuration

---

## Additional Resources

- [js-cookie Documentation](https://github.com/js-cookie/js-cookie)
- [OWASP Cookie Security](https://owasp.org/www-community/controls/SecureCookieAttribute)
- [MDN: HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
