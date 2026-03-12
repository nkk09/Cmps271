"""
JWT token creation and verification.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings

# The data we encode into every token
# sub = user_id, role = their primary role string


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT. Returns the payload dict or None if invalid/expired.
    Also enforces required claims.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require_exp": True, "require_iat": True},  # extra strict
        )

        # Require essential claims
        sub = payload.get("sub")
        role = payload.get("role")

        if not sub or not isinstance(sub, str):
            return None
        if not role or not isinstance(role, str):
            return None

        # Optional: ensure sub is a valid UUID string
        try:
            uuid.UUID(sub)
        except Exception:
            return None

        # Optional: ensure role is in allowed set (if you have one)
        # allowed_roles = {"student", "admin"}  # adapt to your app
        # if role not in allowed_roles:
        #     return None

        return payload

    except JWTError:
        return None
