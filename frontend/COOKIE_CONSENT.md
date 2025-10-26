# 🍪 Cookie Consent Implementation

## Overview

ProctorIQ now implements **GDPR-compliant cookie consent** that asks users for permission before storing authentication cookies. This ensures privacy compliance and gives users control over their data.

---

## Features

### ✅ Cookie Consent Banner
- **Beautiful Material-UI Design** matching existing theme
- **Animated slide-up** from bottom of page
- **Cookie icon** for visual clarity
- **Accept/Decline buttons** for user choice
- **Learn more link** to privacy policy
- **Dismissible** with close button

### ✅ Smart Storage Strategy
- **With Consent:** Uses secure cookies (persistent, 24-hour expiry)
- **Without Consent:** Falls back to sessionStorage (clears on tab close)
- **Hybrid Approach:** Respects user choice while maintaining functionality

### ✅ Privacy Features
- **One-time prompt** (consent remembered for 1 year)
- **Explicit opt-in** required for cookies
- **Clear explanation** of cookie usage
- **Easy decline** option
- **No tracking without consent**

---

## How It Works

### 1. First Visit (No Consent)

```
User visits site
  ↓
Cookie consent banner appears after 1 second
  ↓
User sees: "🍪 We use cookies"
  ↓
User must choose: [Accept All] or [Decline]
```

### 2. User Accepts Cookies

```
User clicks "Accept All"
  ↓
cookie_consent=accepted stored (expires: 1 year)
  ↓
Banner disappears
  ↓
Authentication uses COOKIES (auth_token, user)
  ↓
Session persists across browser restarts
```

### 3. User Declines Cookies

```
User clicks "Decline"
  ↓
cookie_consent=declined stored (expires: 30 days)
  ↓
Banner disappears
  ↓
Authentication uses SESSIONSTORAGE (auth_token, user)
  ↓
Session clears when browser/tab closes
```

---

## Storage Comparison

| Storage Type | With Consent | Without Consent |
|--------------|--------------|-----------------|
| **Auth Token** | Cookie (24h) | sessionStorage |
| **User Data** | Cookie (24h) | sessionStorage |
| **Persistence** | Across restarts | Tab session only |
| **Security** | HttpOnly possible | JavaScript access |
| **GDPR Compliant** | ✅ Yes | ✅ Yes |

---

## Banner Design

### Visual Preview

```
┌─────────────────────────────────────────────────────────────┐
│  🍪    🍪 We use cookies                              ✕     │
│                                                              │
│  ProctorIQ uses cookies to enhance your experience,         │
│  keep you logged in, and remember your preferences.         │
│  We use secure, encrypted cookies that expire after         │
│  24 hours for authentication. By clicking "Accept",         │
│  you agree to our use of cookies. Learn more               │
│                                                              │
│  [  Accept All  ]  [   Decline   ]                         │
└─────────────────────────────────────────────────────────────┘
```

### Styling
- **Background:** White paper with elevation shadow
- **Position:** Fixed bottom, centered, max-width 800px
- **Animation:** Slide up with fade-in
- **Icons:** Cookie icon (primary color) + Close button
- **Buttons:** 
  - Accept: Contained primary button
  - Decline: Outlined button
- **Typography:** Clear, readable text with link styling

---

## Code Implementation

### CookieConsent Component

```tsx
// src/components/CookieConsent.tsx

Key Features:
✅ Checks if consent already given (cookie_consent)
✅ Shows banner after 1-second delay
✅ Accept button: Sets cookie_consent=accepted (1 year)
✅ Decline button: Sets cookie_consent=declined (30 days)
✅ Close button: Same as decline
✅ Collapse animation for smooth UX
```

### AuthContext Integration

```tsx
// src/context/AuthContext.tsx

hasCookieConsent() function:
- Checks: Cookies.get('cookie_consent') === 'accepted'
- Returns: true/false

Login flow:
if (hasCookieConsent()) {
  Cookies.set('auth_token', token);     // Persistent
} else {
  sessionStorage.setItem('auth_token', token);  // Temporary
}

Token retrieval (axios interceptor):
let token = Cookies.get('auth_token');
if (!token) {
  token = sessionStorage.getItem('auth_token');  // Fallback
}
```

---

## User Flow Examples

### Scenario 1: Student Accepts Cookies

1. **Visit site:** http://localhost:3000
2. **See banner:** Cookie consent appears
3. **Click "Accept All"**
4. **Navigate to:** /login
5. **Login as student**
6. **✅ Result:** 
   - Cookies stored: `auth_token`, `user`, `cookie_consent`
   - Can close browser and return → Still logged in
   - Session persists for 24 hours

### Scenario 2: Teacher Declines Cookies

1. **Visit site:** http://localhost:3000
2. **See banner:** Cookie consent appears
3. **Click "Decline"**
4. **Navigate to:** /login
5. **Login as teacher**
6. **✅ Result:**
   - sessionStorage used: `auth_token`, `user`
   - Cookie stored: `cookie_consent=declined` (30 days)
   - Close browser → Logged out
   - Reopen browser → Must login again

### Scenario 3: Returning User (Already Consented)

1. **Visit site:** http://localhost:3000
2. **Banner:** Does NOT appear (consent cookie exists)
3. **Already logged in:** Auto-authenticated from cookies
4. **✅ Result:**
   - Seamless experience
   - No repeated consent prompt
   - Consent remembered for 1 year

---

## Testing Instructions

### Test 1: First Visit with Accept

```bash
# 1. Clear all cookies and storage
# Chrome: DevTools → Application → Clear storage → Clear site data

# 2. Visit site
open http://localhost:3000

# 3. Verify banner appears after 1 second
# Should see: "🍪 We use cookies"

# 4. Click "Accept All"

# 5. Check cookies (DevTools → Application → Cookies)
# Should see:
cookie_consent=accepted; expires=(1 year from now)

# 6. Login and verify auth cookies stored
auth_token=eyJhbGci...; expires=(24h from now)
user={"id":"..."}; expires=(24h from now)
```

### Test 2: First Visit with Decline

```bash
# 1. Clear all cookies and storage

# 2. Visit site
open http://localhost:3000

# 3. Click "Decline"

# 4. Check cookies
cookie_consent=declined; expires=(30 days from now)

# 5. Login

# 6. Check sessionStorage (DevTools → Application → Session Storage)
auth_token: eyJhbGci...
user: {"id":"..."}

# 7. Close browser and reopen → Should be logged out
```

### Test 3: Returning User

```bash
# 1. With cookie_consent=accepted already set

# 2. Visit site
open http://localhost:3000

# 3. Verify: Banner does NOT appear

# 4. Login

# 5. Close and reopen browser

# 6. Visit site again → Should still be logged in
```

---

## Privacy Compliance

### GDPR Requirements

| Requirement | Implementation | Status |
|------------|----------------|--------|
| **Explicit Consent** | User must click "Accept" | ✅ |
| **Clear Information** | Banner explains cookie usage | ✅ |
| **Easy Opt-Out** | "Decline" button prominent | ✅ |
| **Consent Record** | cookie_consent cookie stored | ✅ |
| **No Tracking Without Consent** | sessionStorage fallback | ✅ |
| **Functional Without Cookies** | App works with sessionStorage | ✅ |

### Cookie Details Provided

User is told:
- ✅ **What:** "We use cookies"
- ✅ **Why:** "Enhance experience, keep you logged in, remember preferences"
- ✅ **Type:** "Secure, encrypted cookies"
- ✅ **Duration:** "Expire after 24 hours"
- ✅ **Control:** "Accept or Decline"
- ✅ **More Info:** Link to privacy policy

---

## Customization Options

### Change Banner Text

```tsx
// src/components/CookieConsent.tsx

<Typography variant="body2">
  YOUR CUSTOM TEXT HERE
</Typography>
```

### Change Consent Duration

```tsx
// Accept consent (default: 1 year)
Cookies.set('cookie_consent', 'accepted', {
  expires: 365,  // Change this number
});

// Decline consent (default: 30 days)
Cookies.set('cookie_consent', 'declined', {
  expires: 30,  // Change this number
});
```

### Change Banner Position

```tsx
// Bottom (default)
<Box sx={{ position: 'fixed', bottom: 0 }}>

// Top
<Box sx={{ position: 'fixed', top: 0 }}>

// Center
<Box sx={{ 
  position: 'fixed', 
  top: '50%', 
  transform: 'translateY(-50%)' 
}}>
```

### Change Appearance Delay

```tsx
// Default: 1 second
setTimeout(() => setShowBanner(true), 1000);

// Immediate
setShowBanner(true);

// 3 seconds
setTimeout(() => setShowBanner(true), 3000);
```

---

## Analytics & Tracking

### Monitor Consent Rates

```tsx
// Add to handleAccept()
const handleAccept = () => {
  Cookies.set('cookie_consent', 'accepted', {...});
  
  // Track acceptance (optional)
  console.log('User accepted cookies');
  // analytics.track('cookie_consent_accepted');
  
  setShowBanner(false);
};

// Add to handleDecline()
const handleDecline = () => {
  Cookies.set('cookie_consent', 'declined', {...});
  
  // Track decline (optional)
  console.log('User declined cookies');
  // analytics.track('cookie_consent_declined');
  
  setShowBanner(false);
};
```

### Check Current Consent Status

```tsx
import Cookies from 'js-cookie';

// Get consent status
const consent = Cookies.get('cookie_consent');

console.log('Consent status:', consent);
// Output: 'accepted', 'declined', or undefined
```

---

## Security Considerations

### What's Protected

✅ **Auth tokens stored securely** (HttpOnly possible on backend)
✅ **SameSite=Strict** prevents CSRF attacks  
✅ **Secure flag in production** (HTTPS only)
✅ **No sensitive data in consent cookie**
✅ **sessionStorage fallback** for declined users
✅ **Automatic cleanup** on logout

### Best Practices Followed

1. **Minimal data in cookies** (just token + user object)
2. **Short expiration** (24 hours for auth, 1 year for consent)
3. **Clear text** explaining cookie purpose
4. **Functional without cookies** (sessionStorage works)
5. **User control** (easy to decline)
6. **Privacy-first** (no tracking without consent)

---

## Troubleshooting

### Banner Not Appearing

**Cause:** consent cookie already set  
**Solution:**
```javascript
// Clear consent cookie in browser console
document.cookie = 'cookie_consent=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
// Reload page
```

### Still Showing After Accept

**Cause:** Cookie not being saved  
**Check:**
```javascript
console.log(document.cookie);
// Should include: cookie_consent=accepted
```

### Session Not Persisting

**Cause:** User declined cookies  
**Expected:** sessionStorage clears on tab close  
**Solution:** Ask user to accept cookies for persistent sessions

---

## Related Files

```
frontend/
├── src/
│   ├── components/
│   │   └── CookieConsent.tsx          ← Banner component
│   ├── context/
│   │   └── AuthContext.tsx             ← Consent-aware storage
│   ├── App.tsx                         ← Includes <CookieConsent />
│   └── pages/
│       ├── Login.tsx                   ← Uses AuthContext
│       └── Register.tsx                ← Uses AuthContext
└── COOKIE_AUTHENTICATION.md            ← Technical docs
```

---

## Future Enhancements

### Potential Improvements

1. **Granular Consent**
   - Essential cookies only
   - Performance cookies
   - Marketing cookies
   
2. **Settings Page**
   - View current consent
   - Change preferences
   - View stored cookies

3. **Backend Logging**
   - Track consent rates
   - Compliance reporting
   - Audit trail

4. **Multi-language Support**
   - Translate banner text
   - i18n integration

5. **Remember Me Checkbox**
   - On login form
   - Override consent temporarily

---

## Quick Reference

### Check if Cookies Accepted

```tsx
import Cookies from 'js-cookie';

const hasConsent = Cookies.get('cookie_consent') === 'accepted';
```

### Programmatically Reset Consent

```tsx
// Clear consent (will show banner again)
Cookies.remove('cookie_consent', { path: '/' });
```

### Force Re-prompt

```tsx
// In browser console
Cookies.remove('cookie_consent', { path: '/' });
location.reload();
```

---

## Summary

✅ **GDPR Compliant** cookie consent implemented  
✅ **Beautiful banner** matching existing design  
✅ **Smart fallback** to sessionStorage  
✅ **User choice respected** (accept/decline)  
✅ **One-year consent** memory  
✅ **No repeated prompts** for returning users  
✅ **Fully functional** with or without cookies  
✅ **Privacy-first** approach

**Result:** ProctorIQ now respects user privacy while maintaining full authentication functionality! 🎉
