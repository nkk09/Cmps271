from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Response, Request, HTTPException, status

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

def require_user(request: Request, secret: str) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return _serializer(secret).loads(token)
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
