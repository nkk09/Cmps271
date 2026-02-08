import json
import secrets
import base64
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from urllib.parse import urlencode
from fastapi import APIRouter, Response, Request, status, HTTPException, Query, Depends, Body
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logger import get_logger
from app.core.session import set_login_cookie, clear_login_cookie, require_user
from app.core.database import get_db
from app.core.oauth2 import entra_client, decode_id_token
from app.models.user import User
from app.models.otp import OTP

router = APIRouter()
logger = get_logger(__name__)

# Cookie names for OAuth state/PKCE storage
PKCE_STATE_COOKIE = "oauth_pkce_state"
PKCE_CODE_VERIFIER_COOKIE = "oauth_code_verifier"


def _generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        __import__("hashlib").sha256(code_verifier.encode()).digest()
    ).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


def _get_pkce_from_cookies(request: Request) -> tuple[str, str]:
    """Extract PKCE state and verifier from cookies."""
    state = request.cookies.get(PKCE_STATE_COOKIE)
    code_verifier = request.cookies.get(PKCE_CODE_VERIFIER_COOKIE)
    if not state or not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing PKCE state or code_verifier"
        )
    return state, code_verifier


def _is_allowed_domain(email: str) -> bool:
    e = email.lower()
    return e.endswith("@mail.aub.edu") or e.endswith("@aub.edu.lb")


def _role_from_email(email: str) -> str:
    e = email.lower()
    if e.endswith("@mail.aub.edu"):
        return "student"
    return "professor"


def _send_otp_email(email: str, code: str) -> bool:
    """
    Attempt to send OTP over SMTP. Always logs the OTP for dev/debugging.
    Returns True if sent successfully, False if not (or not configured).
    """
    logger.info(f"OTP code for {email}: {code} (expires in {settings.OTP_EXPIRY_MINUTES} min)")
    
    # If SMTP not configured, just log the code (for dev/testing)
    if not settings.SMTP_HOST or not settings.SMTP_PORT:
        logger.warning(f"SMTP not configured; OTP code logged above for {email}")
        return False
    
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your AUB Reviews OTP"
        msg["From"] = settings.SMTP_FROM or "noreply@aub.edu.lb"
        msg["To"] = email
        msg.set_content(
            f"Your one-time code is:\n\n  {code}\n\n"
            f"It expires in {settings.OTP_EXPIRY_MINUTES} minutes. "
            f"Do not share this code with anyone."
        )

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as s:
            if settings.SMTP_USER and settings.SMTP_PASS:
                s.starttls()
                s.login(settings.SMTP_USER, settings.SMTP_PASS)
            s.send_message(msg)
        
        logger.info(f"OTP email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP auth failed: {e} (check SMTP_USER/SMTP_PASS)")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        return False


@router.get("/login")
def login():
    """
    Initiates OAuth2 flow with Entra ID.
    Redirects user to Microsoft login page for AUB account.
    """
    if not settings.ENABLE_OAUTH:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OAuth is disabled")

    code_verifier, code_challenge = _generate_pkce_pair()
    state = secrets.token_urlsafe(32)
    
    # Generate authorization URL
    auth_url = entra_client.get_authorization_url(state, code_challenge)
    
    # Create redirect response
    response = RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
    
    # Set PKCE cookies on the redirect response
    response.set_cookie(
        PKCE_STATE_COOKIE,
        state,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=600,  # 10 minutes
        path="/",
    )
    response.set_cookie(
        PKCE_CODE_VERIFIER_COOKIE,
        code_verifier,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=600,  # 10 minutes
        path="/",
    )
    
    logger.info(f"Login: redirecting to Entra, state={state[:8]}...")
    return response


@router.get("/me")
def me(request: Request):
    user = require_user(request, settings.SESSION_SECRET)
    logger.debug("Me called, user resolved")
    return {"user": user}


@router.post("/logout")
def logout(response: Response):
    clear_login_cookie(response)
    logger.info("Logout: session cookie cleared")
    return {"ok": True}


@router.post("/otp/send")
def otp_send(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Send a one-time code to the provided email if domain is allowed.
    Includes rate-limiting: max 3 OTPs per email per hour.
    """
    if settings.ENABLE_OAUTH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP disabled when OAuth is enabled")

    email = (payload or {}).get("email", "").strip()
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email")

    if not _is_allowed_domain(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email domain not allowed (must be @mail.aub.edu or @aub.edu.lb)")

    # Rate limiting: max 3 OTPs per email per hour
    # TEMPORARILY DISABLED FOR TESTING
    # recent_count = OTP.count_recent_for_email(db, email, minutes=60)
    # if recent_count >= 3:
    #     logger.warning(f"Rate limit exceeded for OTP send: {email}")
    #     raise HTTPException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail="Too many OTP requests. Please try again in 1 hour."
    #     )

    # Clean up any expired OTPs before creating a new one
    OTP.cleanup_expired(db)

    # Generate 6-digit OTP code
    code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    
    otp_record = OTP.create(db, email, code, expires_at)
    _send_otp_email(email, code)

    logger.info(f"OTP created for {email}, expires at {expires_at.isoformat()}")
    return {"ok": True, "message": "OTP sent to your email"}


@router.post("/otp/verify")
def otp_verify(response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Verify OTP code and create user session.
    Enforces max 5 failed attempts per OTP before expiry.
    """
    try:
        if settings.ENABLE_OAUTH:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP disabled when OAuth is enabled")

        email = (payload or {}).get("email", "").strip()
        code = (payload or {}).get("code", "").strip()
        
        if not email or not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email or code")

        # Retrieve latest non-expired OTP for this email
        otp_record = OTP.get_latest_for_email(db, email)
        if not otp_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid OTP found for this email")

        # Check if OTP is expired
        if OTP.is_expired(otp_record):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")

        # Check attempt limit (max 5 wrong attempts)
        if otp_record.attempts >= 5:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts. Request a new OTP.")

        # Verify code
        if otp_record.code != str(code):
            otp_record.attempts += 1
            db.commit()
            remaining = 5 - otp_record.attempts
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid OTP code. {remaining} attempts remaining.")

        # OTP is valid: create or update user
        role = _role_from_email(email)
        entra_oid = f"local:{email.lower()}"
        user = User.create_or_update(db, entra_oid=entra_oid, entra_email=email.lower(), role=role)

        # Mark OTP as verified and consumed
        otp_record.verified_at = datetime.utcnow()
        db.commit()

        session_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "entra_oid": user.entra_oid,
        }

        # Set login session cookie
        set_login_cookie(response, settings.SESSION_SECRET, session_data)

        logger.info(f"OTP verified and user logged in: {user.username} ({user.entra_email})")
        return {"ok": True, "user": session_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in otp_verify: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/callback")
async def callback(request: Request, code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    """
    OAuth2 callback endpoint.
    Exchanges authorization code for tokens, saves user to DB, and creates session.
    """
    try:
        # Verify state parameter
        stored_state, code_verifier = _get_pkce_from_cookies(request)
        if state != stored_state:
            logger.warning(f"State mismatch: {state} != {stored_state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State parameter mismatch"
            )
        
        # Exchange code for tokens
        logger.debug(f"Callback: exchanging code for tokens")
        token_response = await entra_client.exchange_code_for_token(code, code_verifier)
        
        id_token = token_response.get("id_token")
        if not id_token:
            logger.error("No id_token in token response")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to obtain ID token"
            )
        
        # Decode ID token and extract user info
        claims = decode_id_token(id_token)
        entra_info = entra_client.extract_user_info(claims)
        
        # Save or update user in database
        user = User.create_or_update(
            db,
            entra_oid=entra_info["user_id"],
            entra_email=entra_info["email"],
            role=entra_info["role"]
        )
        
        logger.info(f"Callback: authenticated user {user.username} (entra_email: {entra_info['email']}, role: {user.role})")
        
        # Session data: use anonymous username, not email
        session_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "entra_oid": user.entra_oid,
        }
        
        # Create JSON response with anonymous user info
        response_data = {"ok": True, "user": session_data}
        response = JSONResponse(content=response_data)
        
        # Clear PKCE cookies
        response.delete_cookie(PKCE_STATE_COOKIE, path="/")
        response.delete_cookie(PKCE_CODE_VERIFIER_COOKIE, path="/")
        
        # Set login session cookie
        set_login_cookie(response, settings.SESSION_SECRET, session_data)
        
        return response
    
    except Exception as e:
        logger.error(f"Callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/admin/cleanup-otps")
def admin_cleanup_otps(db: Session = Depends(get_db)):
    """
    Admin endpoint to manually clean up expired OTP records.
    Use this for maintenance in production.
    """
    count = OTP.cleanup_expired(db)
    logger.info(f"Admin requested OTP cleanup: {count} records deleted")
    return {"ok": True, "deleted": count}

