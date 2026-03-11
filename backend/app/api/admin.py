from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas import MuteUserRequest, UserStatusOut

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user: User):
    # If your project uses a roles table instead, tell me and I’ll rewrite this.
    if getattr(user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


@router.post("/users/{user_id}/mute", response_model=UserStatusOut)
def mute_user(
    user_id: str,
    body: MuteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.muted_until = datetime.utcnow() + timedelta(minutes=body.minutes)
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/block", response_model=UserStatusOut)
def block_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/unblock", response_model=UserStatusOut)
def unblock_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = False
    db.commit()
    db.refresh(user)
    return user