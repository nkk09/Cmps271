"""
CRUD operations for Course model.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course


async def get_by_id(db: AsyncSession, course_id: uuid.UUID) -> Optional[Course]:
    result = await db.execute(select(Course).where(Course.id == course_id))
    return result.scalar_one_or_none()


async def get_by_code(db: AsyncSession, code: str) -> Optional[Course]:
    result = await db.execute(select(Course).where(Course.code == code.upper().strip()))
    return result.scalar_one_or_none()


async def get_all(
    db: AsyncSession,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Course]:
    query = select(Course)
    if department:
        query = query.where(Course.department == department)
    query = query.order_by(Course.code).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search(
    db: AsyncSession,
    query_str: str,
    skip: int = 0,
    limit: int = 50,
) -> list[Course]:
    """Search by course code or title (case-insensitive)."""
    pattern = f"%{query_str.strip()}%"
    result = await db.execute(
        select(Course)
        .where(
            Course.code.ilike(pattern) | Course.title.ilike(pattern)
        )
        .order_by(Course.code)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_departments(db: AsyncSession) -> list[str]:
    """Return a sorted list of all distinct departments."""
    result = await db.execute(
        select(Course.department).distinct().order_by(Course.department)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    code: str,
    title: str,
    department: str,
    description: Optional[str] = None,
    attributes: Optional[list[str]] = None,
) -> Course:
    course = Course(
        code=code.upper().strip(),
        title=title,
        department=department,
        description=description,
        attributes=attributes,
    )
    db.add(course)
    await db.flush()
    return course


async def update(
    db: AsyncSession,
    course: Course,
    title: Optional[str] = None,
    description: Optional[str] = None,
    attributes: Optional[list[str]] = None,
) -> Course:
    if title is not None:
        course.title = title
    if description is not None:
        course.description = description
    if attributes is not None:
        course.attributes = attributes
    await db.flush()
    return course


async def delete(db: AsyncSession, course: Course) -> None:
    await db.delete(course)
    await db.flush()
