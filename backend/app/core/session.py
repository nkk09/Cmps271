from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Response, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

COOKIE_NAME = "app_session"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

def _serializer(secret: str) -> URLSafeSerializer:
    return URLSafeSerializer(secret, salt="app-session")

def set_login_cookie(response: Response, secret: str, payload: dict) -> None:
    token = _serializer(secret).dumps(payload)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=False,   # True in prod (HTTPS)
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

def clear_login_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")

def get_session_data(request: Request) -> dict:
    """Extract session data from cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return _serializer(settings.SESSION_SECRET).loads(token)
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

def require_user(
    request: Request,
    db: Session = Depends(get_db),
) -> "User":
    """Get authenticated user from session and database."""
    session_data = get_session_data(request)
    user_id = session_data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user
