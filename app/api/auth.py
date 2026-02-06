import json
import secrets
import base64
from urllib.parse import urlencode
from fastapi import APIRouter, Response, Request, status, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logger import get_logger
from app.core.session import set_login_cookie, clear_login_cookie, require_user
from app.core.database import get_db
from app.core.oauth2 import entra_client, decode_id_token
from app.models.user import User

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


@router.get("/login")
def login():
    """
    Initiates OAuth2 flow with Entra ID.
    Redirects user to Microsoft login page for AUB account.
    """
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
