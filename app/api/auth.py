from fastapi import APIRouter, Response, Request, status
from app.core.config import settings
from app.core.logger import get_logger
from app.core.session import set_login_cookie, clear_login_cookie, require_user

router = APIRouter()
logger = get_logger(__name__)

@router.get("/login")
def login(response: Response):
    """
    TEMP DEV LOGIN:
    sets a session cookie with a fake user.
    We'll replace this with Entra callback later.
    """
    fake_user = {
        "user_id": "dev-user-1",
        "role": "student",
    }
    set_login_cookie(response, settings.SESSION_SECRET, fake_user)
    logger.info("Dev login: session cookie set")
    return {"ok": True, "note": "dev login set cookie"}

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

@router.get("/callback", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def callback():
    """
    Placeholder: will become Entra OAuth callback later.
    """
    logger.info("Auth callback hit (not implemented yet)")
    return {"detail": "Not implemented yet"}
