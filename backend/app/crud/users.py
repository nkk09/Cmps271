"""
CRUD operations for User model.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.encryption import encrypt_field, blind_index


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Look up a user by email using the blind index (never the encrypted column)."""
    idx = blind_index(email)
    result = await db.execute(select(User).where(User.email_index == idx))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, email: str) -> User:
    user = User.make(email=email)
    db.add(user)
    await db.flush()  # get id without committing — caller manages transaction
    return user


async def update_status(db: AsyncSession, user: User, status: str) -> User:
    """status: 'active' | 'suspended' | 'inactive'"""
    user.status = status
    await db.flush()
    return user


async def update_last_login(db: AsyncSession, user: User) -> User:
    user.last_login = datetime.utcnow()
    await db.flush()
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.flush()


async def exists_by_email(db: AsyncSession, email: str) -> bool:
    idx = blind_index(email)
    result = await db.execute(select(User.id).where(User.email_index == idx))
    return result.scalar_one_or_none() is not None
