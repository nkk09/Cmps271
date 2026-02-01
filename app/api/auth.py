from fastapi import APIRouter, Response, status
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/login", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def login():
    """
    Start Entra OIDC login (redirect to Microsoft).
    """
    logger.info("Auth login requested (not implemented yet)")
    return {"detail": "Not implemented yet"}

@router.get("/callback", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def callback():
    """
    OAuth callback endpoint (Microsoft redirects here).
    """
    logger.info("Auth callback hit (not implemented yet)")
    return {"detail": "Not implemented yet"}

@router.get("/me", status_code=status.HTTP_401_UNAUTHORIZED)
def me():
    """
    Return the current logged-in user.
    For now: always unauthenticated until we implement sessions.
    """
    logger.debug("Auth me requested (unauthenticated in skeleton)")
    return {"detail": "Not authenticated"}

@router.post("/logout")
def logout(response: Response):
    """
    Clear session cookie (later).
    For now: just return ok.
    """
    logger.info("Auth logout requested")
    # later: response.delete_cookie("session")
    return {"ok": True}
