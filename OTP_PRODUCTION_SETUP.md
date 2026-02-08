# OTP Authentication System - Production Setup Guide

## Overview

The app now supports two authentication modes:
1. **OAuth2 with Entra ID** (original, gated by `ENABLE_OAUTH=true`)
2. **Email OTP** (new, default when `ENABLE_OAUTH=false`)

The OTP system is **production-ready** with:
- ✅ Persistent database storage (no in-memory state)
- ✅ Rate-limiting (max 3 requests per email per hour)
- ✅ Attempt limiting (max 5 failed verifications per OTP)
- ✅ Automatic expiry (configurable, default 10 minutes)
- ✅ Automatic cleanup of expired OTPs
- ✅ Optional SMTP email sending (falls back to logging for dev)
- ✅ Proper error handling and logging

---

## Environment Configuration

### Minimal Setup (Development)

Create/update your `.env` file:

```bash
# App settings
APP_NAME=AUB Reviews
ENV=dev

# Session
SESSION_SECRET=your-very-secure-secret-change-me

# Database
DATABASE_URL=sqlite:///./aub_reviews.db

# Authentication Mode (OTP is default)
ENABLE_OAUTH=false

# OTP Settings
OTP_EXPIRY_MINUTES=10

# SMTP is optional in dev (OTPs logged to console otherwise)
# Uncomment to enable email sending:
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASS=your-app-password
# SMTP_FROM=noreply@aub.edu.lb
```

### Production Setup

For production, enable SMTP and configure:

```bash
# ... same as above, but:

ENV=prod
SESSION_SECRET=generate-a-strong-random-key

# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:password@localhost/aub_reviews

# Email Configuration (required for production)
SMTP_HOST=smtp.gmail.com                 # or your mail provider
SMTP_PORT=587                             # 587 for TLS, 465 for SSL
SMTP_USER=your-app-email@gmail.com
SMTP_PASS=your-app-password              # use app-specific password for Gmail
SMTP_FROM=noreply@aub.edu.lb

OTP_EXPIRY_MINUTES=10                    # stay reasonable to prevent brute force
```

**Gmail App Password Setup:**
1. Enable 2FA on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password for "Mail" → "Windows" (or your OS)
4. Use this in `SMTP_PASS` (not your regular password)

---

## API Endpoints

### Send OTP

**Request:**
```bash
POST /auth/otp/send
Content-Type: application/json

{
  "email": "username@mail.aub.edu"  # or @aub.edu.lb
}
```

**Response (success):**
```json
{
  "ok": true,
  "message": "OTP sent to your email"
}
```

**Possible errors:**
- `400 Bad Request` – Missing email, invalid domain, or too many requests (rate limit)
- `429 Too Many Requests` – >3 OTP requests per email per hour

In dev mode (no SMTP), the OTP is logged to console. Example log:
```
OTP code for student@mail.aub.edu: 123456 (expires in 10 min)
```

### Verify OTP

**Request:**
```bash
POST /auth/otp/verify
Content-Type: application/json

{
  "email": "username@mail.aub.edu",
  "code": "123456"
}
```

**Response (success):**
```json
{
  "ok": true,
  "user": {
    "user_id": 1,
    "username": "ColorfulFlower123",
    "role": "student",
    "entra_oid": "local:username@mail.aub.edu"
  }
}
```

Session cookie is automatically set. Subsequent requests include the cookie for authentication.

**Possible errors:**
- `400 Bad Request` – Missing fields, no OTP found, OTP expired, or invalid code
- `429 Too Many Requests` – >5 failed attempts on the same OTP

---

## Database Models

### OTP Record

```
- id: primary key
- email: (indexed) user's email
- code: 6-digit OTP code
- attempts: count of failed verification attempts
- created_at: timestamp
- expires_at: (indexed) expiry time
- verified_at: timestamp when successfully verified (or NULL)
```

**Automatic cleanup:** Expired OTP records are deleted automatically on startup and periodically.

### User Record

Existing model; no changes. Users are created/updated on OTP verification with:
- `entra_oid = "local:<email>"` (identifies OTP users)
- `entra_email = "<user's email>"`
- `role = "student"` (for @mail.aub.edu) or `"professor"` (for @aub.edu.lb)

---

## Background Tasks

### Automatic Cleanup (Default)

On app startup, all expired OTPs are deleted automatically.

### Optional: Periodic Cleanup with APScheduler

For production, optionally enable periodic cleanup (every 30 min):

1. **Install APScheduler:**
   ```bash
   pip install apscheduler
   ```

2. **Update `app/main.py`** (optional, for automatic scheduling):
   ```python
   from app.core.scheduler import setup_scheduler
   
   @app.on_event("startup")
   def startup_event():
       init_db()
       cleanup_expired_otps()  # one-time on startup
       setup_scheduler()       # add this for periodic cleanup
   ```

3. **Or use manual trigger (any time):**
   ```bash
   POST /auth/admin/cleanup-otps
   ```

---

## Role Detection

Email domain → automatic role assignment:

| Email Domain | Role |
|---|---|
| `*@mail.aub.edu` | `student` |
| `*@aub.edu.lb` | `professor` |

Both domains allowed. Any other domain is rejected.

---

## Security Features

✅ **Rate Limiting:**
- Max 3 OTP sends per email per hour
- Max 5 failed verification attempts per OTP
- Helps prevent brute force attacks

✅ **Expiry:**
- OTPs expire after `OTP_EXPIRY_MINUTES` (default 10 min)
- Expired OTPs are cleaned up automatically

✅ **Validation:**
- Email domain whitelist (@mail.aub.edu, @aub.edu.lb)
- 6-digit alphanumeric code
- Attempt counter prevents guessing

✅ **Logging:**
- All OTP events logged (send, verify, expired, failed attempts)
- Helpful for debugging and audit trails

---

## Switching Between OAuth and OTP

To **re-enable original OAuth flow** when you have the Entra tenant ID:

1. Set `ENABLE_OAUTH=true` in `.env`
2. Configure Entra settings:
   ```bash
   ENTRA_TENANT_ID=your-tenant-id
   ENTRA_CLIENT_ID=your-client-id
   ENTRA_CLIENT_SECRET=your-client-secret
   ENTRA_REDIRECT_URI=http://localhost:8000/auth/callback
   ```
3. Restart app

OTP endpoints will return `400 Bad Request` when OAuth is enabled.

---

## Testing OTP Flow Locally

### Using curl:

```bash
# 1. Send OTP
curl -X POST http://localhost:8000/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{"email":"student@mail.aub.edu"}'

# Check console log for OTP code (e.g., 123456)

# 2. Verify OTP
curl -X POST http://localhost:8000/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"email":"student@mail.aub.edu","code":"123456"}' \
  -c cookies.txt

# 3. Check authenticated user
curl http://localhost:8000/auth/me -b cookies.txt
```

### Using Python:

```python
import requests

base = "http://localhost:8000"
email = "student@mail.aub.edu"

# Send OTP
r = requests.post(f"{base}/auth/otp/send", json={"email": email})
print(r.json())

# Check app logs for code, or check DB for OTP record

# Verify OTP
r = requests.post(f"{base}/auth/otp/verify", 
                  json={"email": email, "code": "123456"})
print(r.json())
print(r.cookies)  # session cookie

# Check authenticated user
r = requests.get(f"{base}/auth/me", cookies=r.cookies)
print(r.json())
```

---

## Production Checklist

- [ ] Set `ENV=prod` in `.env`
- [ ] Generate strong `SESSION_SECRET` (use `secrets.token_urlsafe(32)`)
- [ ] Configure SMTP (Gmail, SendGrid, or your provider)
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set `SESSION_SECRET` to something long and random
- [ ] Test email delivery with a real account first
- [ ] Enable HTTPS (`secure=True` in cookie settings)
- [ ] Monitor logs for failed OTP attempts
- [ ] Optional: Install & enable APScheduler for periodic cleanup
- [ ] Optional: Set tighter `OTP_EXPIRY_MINUTES` (5-10 min recommended)
- [ ] Document any custom role-assignment logic beyond email domain

---

## Troubleshooting

**"SMTP credentials invalid"**
→ Check `SMTP_USER` and `SMTP_PASS` in `.env`; use app-specific password for Gmail.

**"OTP not sent"**
→ Check `SMTP_HOST` and `SMTP_PORT` in `.env`; see logs for errors.

**"Too many OTP requests"**
→ User hit rate limit (3 per hour). They'll need to wait or try another email.

**"OTP expired"**
→ Reduce `OTP_EXPIRY_MINUTES` or remind users to verify quickly.

**"database locked" (SQLite)**
→ Upgrade to PostgreSQL for production to avoid concurrent write issues.

---

## Files Changed

- **new:** `app/models/otp.py` – OTP database model
- **new:** `app/core/tasks.py` – Background task helpers
- **new:** `app/core/scheduler.py` – Optional APScheduler setup
- **updated:** `app/api/auth.py` – OTP endpoints + admin cleanup
- **updated:** `app/core/config.py` – OTP/SMTP config flags
- **updated:** `app/core/oauth2.py` – Conditional Entra client init
- **updated:** `app/main.py` – OTP cleanup on startup

---

## Next Steps

1. Update `.env` with your SMTP credentials
2. Run app: `uvicorn app.main:app --reload`
3. Test `/auth/otp/send` and `/auth/otp/verify`
4. Deploy to production with PostgreSQL and real SMTP
5. (Optional) Install APScheduler for periodic cleanup
