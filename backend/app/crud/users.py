"""
CRUD operations for User model.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.student import Student
from app.models.professor import Professor
from app.models.role import Role, UserRole
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


async def list_for_admin(
    db: AsyncSession,
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[User]:
    query = (
        select(User)
        .options(selectinload(User.student), selectinload(User.professor))
        .order_by(User.created_at.desc())
    )

    if role:
        query = (
            query.join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.role == role)
        )

    if status:
        query = query.where(User.status == status)

    if search:
        like = f"%{search.lower()}%"
        query = (
            query.outerjoin(Student, Student.user_id == User.id)
            .outerjoin(Professor, Professor.user_id == User.id)
            .where(
                or_(
                    func.lower(Student.username).like(like),
                    func.lower(Professor.first_name).like(like),
                    func.lower(Professor.last_name).like(like),
                )
            )
        )

    result = await db.execute(query.distinct().offset(skip).limit(limit))
    return list(result.scalars().all())
