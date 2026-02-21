"""
User profile endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.session import require_user
from app.models.user import User
from app.schemas.user import CurrentUserResponse, UserResponse

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user(
    current_user: User = Depends(require_user),
):
    """Get current user profile (includes email)."""
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        entra_email=current_user.entra_email,
        created_at=current_user.created_at,
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get public user profile (anonymized - only username visible)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
    )
