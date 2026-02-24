"""
FastAPI dependencies.
Injected via Depends() in route functions.
"""

import uuid
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.jwt import decode_access_token
from app.models.user import User
from app.models.student import Student
from app.models.professor import Professor
from app import crud

bearer_scheme = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# DB session (re-exported here so routes only need to import from deps)
# ---------------------------------------------------------------------------

DBDep = Annotated[AsyncSession, Depends(get_db)]


# ---------------------------------------------------------------------------
# Auth dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    db: DBDep,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> User:
    """
    Decode the Bearer JWT and return the authenticated User.
    Raises 401 if token is missing, invalid, or user not found.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = uuid.UUID(payload["sub"])
    user = await crud.users.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended or inactive")

    return user


async def get_current_user_optional(
    db: DBDep,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> Optional[User]:
    """Like get_current_user but returns None instead of raising for unauthenticated requests."""
    if credentials is None:
        return None
    try:
        return await get_current_user(db, credentials)
    except HTTPException:
        return None


async def get_current_student(
    db: DBDep,
    user: Annotated[User, Depends(get_current_user)],
) -> Student:
    """Require the current user to have a student profile."""
    student = await crud.students.get_by_user_id(db, user.id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A student profile is required for this action",
        )
    return student


async def get_current_professor(
    db: DBDep,
    user: Annotated[User, Depends(get_current_user)],
) -> Professor:
    """Require the current user to have a professor profile."""
    professor = await crud.professors.get_by_user_id(db, user.id)
    if professor is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A professor profile is required for this action",
        )
    return professor


async def require_admin(
    db: DBDep,
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require the current user to have the 'admin' role."""
    has_admin = await crud.roles.user_has_permission(db, user.id, "admin")
    if not has_admin:
        is_admin_role = "admin" in [r.role for r in await crud.roles.get_user_roles(db, user.id)]
        if not is_admin_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


# Annotated shortcuts for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[User], Depends(get_current_user_optional)]
CurrentStudent = Annotated[Student, Depends(get_current_student)]
CurrentProfessor = Annotated[Professor, Depends(get_current_professor)]
AdminUser = Annotated[User, Depends(require_admin)]
