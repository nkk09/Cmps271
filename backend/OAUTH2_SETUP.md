# OAuth2 Setup Guide - Entra ID Integration

## Overview
This project implements OAuth2 authentication using Microsoft Entra ID (Azure AD). Users can sign in with their AUB Microsoft email without needing to create a separate account or store passwords.

## How It Works

### OAuth2 Flow (PKCE)
1. **Login Initiate**: User clicks "Login" → `/auth/login`
2. **Generate & Store**: App generates PKCE challenge/state and stores in secure cookies
3. **Redirect to Microsoft**: User redirected to Microsoft login
4. **User Authenticates**: User signs in with AUB email (handled by Microsoft)
5. **Callback**: Microsoft redirects back to `/auth/callback` with authorization code
6. **Exchange Token**: App exchanges code for ID token using PKCE verifier
7. **Create Session**: App extracts user info and sets session cookie
8. **Authenticated**: User is now logged in

### Security Features
- **PKCE**: Proof Key for Code Exchange prevents authorization code interception
- **State Parameter**: Prevents CSRF attacks
- **HttpOnly Cookies**: Session cookies cannot be accessed by JavaScript
- **Short TTL**: PKCE state expires in 10 minutes

## Setup Instructions

### 1. Configure Entra ID App Registration

Go to [Azure Portal](https://portal.azure.com):

1. Navigate to **Azure Active Directory → App Registrations**
2. Click **New registration**
3. Name: `AUB Reviews` (or your app name)
4. Supported account types: **Accounts in any organizational directory (Any Azure AD directory - Multitenant)**
5. Redirect URI: **Web** - `http://localhost:8000/auth/callback`
6. Click **Register**

### 2. Configure Application Settings

In your app registration:

1. Go to **Overview**, copy:
   - **Tenant ID** → `ENTRA_TENANT_ID`
   - **Client ID** → `ENTRA_CLIENT_ID`

2. Go to **Certificates & secrets**:
   - Click **New client secret**
   - Description: `Dev secret`
   - Expires: `6 months` (or longer for dev)
   - Copy the secret value → `ENTRA_CLIENT_SECRET`

3. Go to **Authentication**:
   - Ensure Redirect URI is: `http://localhost:8000/auth/callback`
   - Enable **Access tokens** and **ID tokens** under Implicit grant

4. Go to **API Permissions** (optional, for role detection):
   - Add permission: `user.read`
   - May need to configure app roles or groups for professor detection

### 3. Create `.env` File

Copy `.env.example` to `.env` and fill in your values:

```env
ENV=dev
ENTRA_TENANT_ID=your-tenant-id
ENTRA_CLIENT_ID=your-client-id
ENTRA_CLIENT_SECRET=your-client-secret
ENTRA_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=your-random-secret-here
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000`

## API Endpoints

### POST `/auth/login`
Initiates OAuth2 flow. User will be redirected to Microsoft login.

**Response**: Redirect to Microsoft Entra ID

### GET `/auth/callback`
OAuth2 callback endpoint. Called by Microsoft after user authentication.

**Query Parameters**:
- `code`: Authorization code from Microsoft
- `state`: CSRF protection parameter

**Response**:
```json
{
  "ok": true,
  "user": {
    "user_id": "oid-from-entra",
    "email": "student@aub.edu.lb",
    "name": "John Doe",
    "role": "student",
    "tenant_id": "tenant-id"
  }
}
```

### GET `/auth/me`
Get current authenticated user info.

**Response**:
```json
{
  "user": {
    "user_id": "...",
    "email": "...",
    "role": "..."
  }
}
```

### POST `/auth/logout`
Logs out user by clearing session cookie.

**Response**: `{"ok": true}`

## Testing Locally

### 1. Start the app
```bash
uvicorn app.main:app --reload
```

### 2. Test login flow
1. Open browser: `http://localhost:8000/auth/login`
2. You'll be redirected to Microsoft login
3. Sign in with your AUB Microsoft account
4. After successful auth, you'll return to `/auth/callback` with user info

### 3. Test protected endpoint
1. Call `/auth/me` to get current user
2. Should return your authenticated user info
3. Without login, returns 401 Unauthorized

### 4. Test logout
1. Call POST `/auth/logout`
2. Session cookie will be cleared
3. Subsequent calls to `/auth/me` will return 401

## Production Deployment

Before deploying to production:

1. **Change Redirect URI**: Update `ENTRA_REDIRECT_URI` to your production domain
   - E.g., `https://reviews.aub.edu.lb/auth/callback`

2. **Update Cookie Security**:
   - Set `secure=True` in session middleware
   - Set `https_only=True` in `app.core.session`

3. **Use Strong Session Secret**:
   - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Use in `SESSION_SECRET` env var

4. **Enable HTTPS**: Redirect URI must be HTTPS in production

5. **Configure Real Entra ID Tenant**: Get official credentials from AUB's IT department

## Role Detection

Currently, role is determined by checking if "professor" is in the email. 

For production with AUB, you can enhance this by:

1. **Using Azure AD Groups**:
   - Create groups in Entra ID (e.g., "Professors", "Students")
   - Assign users to groups
   - Read `groups` claim from ID token

2. **Using App Roles**:
   - Define roles in App registration
   - Assign users to roles
   - Read `roles` claim from ID token

See `app.core.oauth2.py:extract_user_info()` for implementation details.

## Troubleshooting

### "PKCE state or code_verifier missing"
- Cookie deletion issue, try clearing browser cookies
- Check `secure=False` is set for local development

### "State parameter mismatch"
- CSRF attack attempt OR session expired
- Check state cookie TTL (currently 10 minutes)

### "Invalid client ID or Client Secret"
- Double-check values in `.env` file
- Ensure they match your Entra ID app registration

### "Redirect URI mismatch"
- Ensure `ENTRA_REDIRECT_URI` in `.env` matches redirect URI in app registration
- Remove trailing slashes

## Files Modified/Created

- `app/core/oauth2.py` - OAuth2 client and helpers
- `app/api/auth.py` - Login, callback, and session endpoints
- `.env.example` - Configuration template

## Next Steps

- [ ] Add role-based access control (RBAC) for endpoints
- [ ] Add frontend login UI
- [ ] Configure Azure AD groups for professor/student roles
- [ ] Add token refresh logic for long-lived sessions
- [ ] Test with real AUB Entra ID tenant
