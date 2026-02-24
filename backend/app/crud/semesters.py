"""
CRUD operations for Semester model.
Semesters are mostly read-only at runtime — created by admins or seeding.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.semester import Semester


async def get_by_id(db: AsyncSession, semester_id: uuid.UUID) -> Optional[Semester]:
    result = await db.execute(select(Semester).where(Semester.id == semester_id))
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Optional[Semester]:
    result = await db.execute(select(Semester).where(Semester.name == name))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> list[Semester]:
    result = await db.execute(select(Semester).order_by(Semester.starts_on.desc()))
    return list(result.scalars().all())


async def get_current(db: AsyncSession) -> Optional[Semester]:
    """Return the semester whose date range contains today."""
    now = datetime.utcnow()
    result = await db.execute(
        select(Semester).where(
            Semester.starts_on <= now,
            Semester.ends_on >= now,
        )
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    name: str,
    starts_on: datetime,
    ends_on: datetime,
) -> Semester:
    semester = Semester(name=name, starts_on=starts_on, ends_on=ends_on)
    db.add(semester)
    await db.flush()
    return semester


async def delete(db: AsyncSession, semester: Semester) -> None:
    await db.delete(semester)
    await db.flush()
