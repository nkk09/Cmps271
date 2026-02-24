"""
Auth routes — Microsoft Entra ID OAuth2 + OTP email fallback.

Entra flow (primary):
  1. GET  /auth/login      → redirect to Microsoft login page
  2. GET  /auth/callback   → exchange code for token, return JWT

OTP flow (fallback if ENABLE_OAUTH=false):
  1. POST /auth/request-otp → send code by email
  2. POST /auth/verify-otp  → verify code, return JWT

  3. POST /auth/logout      → client discards JWT (stateless)

Privacy rules:
  - Plaintext email addresses are NEVER written to logs.
  - All log lines that reference a user identity use the HMAC blind index only.
"""

import asyncio
import hashlib
import hmac as hmac_mod
import os
import secrets
import smtplib
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.dependencies import DBDep
from app.schemas import OTPRequest, OTPVerify, TokenResponse
from app.core.jwt import create_access_token
from app.core.config import settings
from app.core.encryption import blind_index
from app.core.oauth2 import entra_client, decode_id_token
from app.core.logger import get_logger
from app import crud

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# In-process PKCE / state store
# Each entry: { "code_verifier": str, "expires_at": float }
# Entries are tiny and short-lived (5 min); cleaned up on each /login hit.
# ---------------------------------------------------------------------------
_pending_states: dict[str, dict] = {}
_STATE_TTL = 300  # seconds


def _pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge) using S256 method."""
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _purge_stale_states() -> None:
    import time
    now = time.time()
    stale = [k for k, v in _pending_states.items() if v["expires_at"] < now]
    for k in stale:
        del _pending_states[k]


# ---------------------------------------------------------------------------
# Entra OAuth2 routes
# ---------------------------------------------------------------------------

@router.get("/login")
async def login():
    """
    Redirect the user to the Microsoft Entra ID login page.
    Requires ENABLE_OAUTH=true and all ENTRA_* variables set in .env.
    """
    if not entra_client:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OAuth is not enabled. Set ENABLE_OAUTH=true in .env.",
        )

    import time
    _purge_stale_states()

    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = _pkce_pair()

    _pending_states[state] = {
        "code_verifier": code_verifier,
        "expires_at": time.time() + _STATE_TTL,
    }

    url = entra_client.get_authorization_url(state=state, code_challenge=code_challenge)
    return RedirectResponse(url=url, status_code=302)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: DBDep = None,
):
    """
    Handle the redirect back from Microsoft after the user authenticates.
    Exchanges the authorization code for tokens, creates or retrieves the user,
    and returns a JWT — same shape as the OTP verify endpoint.
    """
    if not entra_client:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OAuth is not enabled.",
        )

    # Validate state and retrieve PKCE verifier
    entry = _pending_states.pop(state, None)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state. Please try logging in again.",
        )

    import time
    if entry["expires_at"] < time.time():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state expired. Please try logging in again.",
        )

    # Exchange code for tokens
    try:
        token_response = await entra_client.exchange_code_for_token(
            code=code,
            code_verifier=entry["code_verifier"],
        )
    except Exception as e:
        logger.error(f"Entra token exchange failed: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange authorization code. Please try again.",
        )

    # Decode the ID token to get user claims
    id_token = token_response.get("id_token")
    if not id_token:
        logger.error("Entra token response missing id_token")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No ID token in response from Microsoft.",
        )

    try:
        claims = decode_id_token(id_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode Microsoft ID token.",
        )

    email = (claims.get("email") or claims.get("preferred_username") or "").lower().strip()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email address returned by Microsoft.",
        )

    # Determine role from AUB email domain
    if email.endswith("@mail.aub.edu"):
        role_name = "student"
    elif email.endswith("@aub.edu.lb"):
        role_name = "professor"
    else:
        logger.warning(f"OAuth login rejected — unrecognised email domain, index={blind_index(email)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AUB email addresses (@mail.aub.edu or @aub.edu.lb) are allowed.",
        )

    idx = blind_index(email)

    # Get or create user
    user = await crud.users.get_by_email(db, email)
    is_new = user is None

    if is_new:
        user = await crud.users.create(db, email=email)

        if role_name == "student":
            await crud.students.create(db, user_id=user.id)
        else:
            # Professor accounts are created but need to be linked to a
            # professor record manually (or via an admin flow later).
            pass

        role = await crud.roles.get_role_by_name(db, role_name)
        if role:
            await crud.roles.assign_role_to_user(db, user_id=user.id, role_id=role.id)

        logger.info(f"New user created via OAuth — role={role_name} email_index={idx}")

    await crud.users.update_last_login(db, user)
    await db.commit()

    roles = await crud.roles.get_user_roles(db, user.id)
    primary_role = roles[0].role if roles else role_name

    token = create_access_token(user_id=user.id, role=primary_role)
    logger.info(f"OAuth login successful — email_index={idx}")

    # Redirect to frontend with token in query param.
    # The frontend reads it once, stores it in localStorage, then cleans the URL.
    frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
    redirect_url = f"{frontend_url}/auth/callback?token={token}"
    return RedirectResponse(url=redirect_url, status_code=302)


# ---------------------------------------------------------------------------
# OTP routes (fallback when ENABLE_OAUTH=false)
# ---------------------------------------------------------------------------

@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(body: OTPRequest, db: DBDep):
    """
    Request an OTP for the given email. The code is sent by email.
    Rate-limited. Returns 200 regardless of email existence to prevent enumeration.
    """
    email = body.email.lower().strip()
    idx = blind_index(email)

    # If OAuth is enabled we short-circuit to the Entra login flow.
    # Only allow AUB student emails for OAuth-initiated sign-in.
    if settings.ENABLE_OAUTH:
        if not entra_client:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="OAuth is not enabled. Check ENTRA_ settings in .env.",
            )

        # Accept only student AUB emails for this path as requested
        if not email.endswith("@mail.aub.edu"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="OAuth sign-in is only allowed for @mail.aub.edu addresses.",
            )

        # Create PKCE + state and store it so /callback can validate
        import time
        _purge_stale_states()
        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = _pkce_pair()
        _pending_states[state] = {
            "code_verifier": code_verifier,
            "expires_at": time.time() + _STATE_TTL,
        }

        auth_url = entra_client.get_authorization_url(state=state, code_challenge=code_challenge, login_hint=email)
        return {"oauth": True, "auth_url": auth_url}

    if await crud.otps.is_rate_limited(db, email):
        logger.warning(f"OTP rate limit hit — email_index={idx}")
        return {"message": "If this email is registered, a code has been sent."}

    otp, plain_code = await crud.otps.create(db, email=email)
    await db.commit()

    sent = await _send_otp_email(email, plain_code)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send OTP email. Check SMTP settings in .env.",
        )

    logger.info(f"OTP issued — email_index={idx}")
    return {"message": "A verification code has been sent to your email."}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: OTPVerify, db: DBDep):
    """
    Verify an OTP code. On success, returns a JWT access token.
    New users get a student profile created automatically.
    """
    email = body.email.lower().strip()
    idx = blind_index(email)

    success, otp, error = await crud.otps.verify(db, email=email, plain_code=body.code)

    if not success:
        error_messages = {
            "not_found":    "No active OTP found for this email. Please request a new code.",
            "expired":      "This code has expired. Please request a new one.",
            "max_attempts": "Too many failed attempts. Please request a new code.",
            "invalid_code": "Invalid code.",
        }
        logger.warning(f"OTP verification failed ({error}) — email_index={idx}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_messages.get(error, "Verification failed."),
        )

    user = await crud.users.get_by_email(db, email)
    is_new = user is None

    if is_new:
        user = await crud.users.create(db, email=email)
        await crud.students.create(db, user_id=user.id)
        role = await crud.roles.get_role_by_name(db, "student")
        if role:
            await crud.roles.assign_role_to_user(db, user_id=user.id, role_id=role.id)
        logger.info(f"New user created via OTP — email_index={idx}")

    await crud.users.update_last_login(db, user)

    if otp and otp.user_id is None:
        otp.user_id = user.id

    await db.commit()

    roles = await crud.roles.get_user_roles(db, user.id)
    primary_role = roles[0].role if roles else "student"

    token = create_access_token(user_id=user.id, role=primary_role)
    logger.info(f"OTP verified, token issued — email_index={idx}")
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """Logout — JWT is stateless, client discards the token."""
    return {"message": "Logged out successfully."}


# ---------------------------------------------------------------------------
# Email sending helper (OTP only)
# ---------------------------------------------------------------------------

async def _send_otp_email(email: str, code: str) -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASS]):
        logger.error("SMTP not fully configured — set SMTP_HOST/PORT/USER/PASS in .env")
        return False

    def _send_blocking():
        msg = MIMEText(
            f"Your {settings.APP_NAME} verification code is: {code}\n\n"
            f"This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n"
            f"If you didn't request this, you can safely ignore this email."
        )
        msg["Subject"] = f"Your {settings.APP_NAME} verification code"
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = email

        with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT)) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)

    idx = blind_index(email)
    try:
        await asyncio.get_event_loop().run_in_executor(None, _send_blocking)
        logger.info(f"OTP email delivered — email_index={idx}")
        return True
    except Exception as e:
        logger.error(f"OTP email delivery failed — email_index={idx} — {type(e).__name__}: {e}")
        return False