"""
Auth routes — OTP-based email authentication.

Flow:
  1. POST /auth/request-otp  → generates OTP, sends email (or logs in dev)
  2. POST /auth/verify-otp   → verifies code, returns JWT
  3. POST /auth/logout       → client discards token (stateless)
"""

import logging
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DBDep
from app.schemas import OTPRequest, OTPVerify, TokenResponse
from app.core.jwt import create_access_token
from app.core.config import settings
from app import crud

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(body: OTPRequest, db: DBDep):
    """
    Request an OTP for the given email.
    Rate limited to 5 requests per hour per email.
    Always returns 200 to avoid email enumeration.
    """
    email = body.email.lower().strip()

    # Rate limiting
    if await crud.otps.is_rate_limited(db, email):
        # Still return 200 — don't reveal whether email exists
        logger.warning(f"OTP rate limit hit for email_index={crud.otps._blind(email)}")
        return {"message": "If this email is registered, a code has been sent."}

    # Create OTP
    otp, plain_code = await crud.otps.create(db, email=email)

    # Send or log the code
    await _send_otp(email, plain_code)

    await db.commit()
    return {"message": "If this email is registered, a code has been sent."}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: OTPVerify, db: DBDep):
    """
    Verify an OTP code. On success, returns a JWT access token.
    If the email is new, a user + student profile are created automatically.
    """
    email = body.email.lower().strip()

    success, otp, error = await crud.otps.verify(db, email=email, plain_code=body.code)

    if not success:
        error_messages = {
            "not_found": "No active OTP found for this email.",
            "expired": "This code has expired. Please request a new one.",
            "max_attempts": "Too many failed attempts. Please request a new code.",
            "invalid_code": "Invalid code.",
        }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_messages.get(error, "Verification failed."),
        )

    # Get or create user
    user = await crud.users.get_by_email(db, email)
    is_new = user is None

    if is_new:
        user = await crud.users.create(db, email=email)
        # Auto-create a student profile for new users
        await crud.students.create(db, user_id=user.id)
        # Assign default 'student' role
        role = await crud.roles.get_role_by_name(db, "student")
        if role:
            await crud.roles.assign_role_to_user(db, user_id=user.id, role_id=role.id)

    await crud.users.update_last_login(db, user)

    # Link OTP to user if not already linked
    if otp and otp.user_id is None:
        otp.user_id = user.id

    await db.commit()

    # Get role for JWT
    roles = await crud.roles.get_user_roles(db, user.id)
    primary_role = roles[0].role if roles else "student"

    token = create_access_token(user_id=user.id, role=primary_role)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Logout — JWTs are stateless so the client simply discards the token.
    This endpoint exists for API completeness and future blocklist support.
    """
    return {"message": "Logged out successfully."}


# ---------------------------------------------------------------------------
# Email sending helper
# ---------------------------------------------------------------------------

async def _send_otp(email: str, code: str) -> None:
    """Send OTP via SMTP if configured, otherwise log it (dev mode)."""
    if not settings.SMTP_HOST:
        logger.info(f"[DEV] OTP for {email}: {code}")
        return

    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(
            f"Your {settings.APP_NAME} verification code is: {code}\n\n"
            f"This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n"
            f"If you didn't request this, you can ignore this email."
        )
        msg["Subject"] = f"Your {settings.APP_NAME} verification code"
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = email

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASS:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        # Don't raise — OTP is still created, user can retry
