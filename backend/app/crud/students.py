"""
CRUD operations for Student model.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student, generate_unique_username


async def get_by_id(db: AsyncSession, student_id: uuid.UUID) -> Optional[Student]:
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()


async def get_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[Student]:
    result = await db.execute(select(Student).where(Student.user_id == user_id))
    return result.scalar_one_or_none()


async def get_by_username(db: AsyncSession, username: str) -> Optional[Student]:
    result = await db.execute(select(Student).where(Student.username == username))
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    user_id: uuid.UUID,
    major: Optional[str] = None,
) -> Student:
    """
    Create a student profile for an existing user.
    Username is auto-generated anonymously.
    """
    # generate_unique_username uses a sync session internally;
    # for async we replicate the uniqueness check here
    username = await _generate_unique_username(db)
    student = Student(
        user_id=user_id,
        username=username,
        major=major,
    )
    db.add(student)
    await db.flush()
    return student


async def _generate_unique_username(db: AsyncSession) -> str:
    """Async-safe unique username generation."""
    import random
    import secrets
    from app.models.student import _ADJECTIVES, _NOUNS

    for _ in range(100):
        adj = random.choice(_ADJECTIVES).capitalize()
        noun = random.choice(_NOUNS).capitalize()
        number = random.randint(0, 9999)
        username = f"{adj}{noun}{number}"
        result = await db.execute(select(Student.id).where(Student.username == username))
        if result.scalar_one_or_none() is None:
            return username

    return f"User{secrets.token_hex(8)}"


async def update_major(db: AsyncSession, student: Student, major: str) -> Student:
    student.major = major
    await db.flush()
    return student


async def delete(db: AsyncSession, student: Student) -> None:
    await db.delete(student)
    await db.flush()
