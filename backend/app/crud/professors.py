"""
CRUD operations for Professor model.
"""

import uuid
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.professor import Professor
from app.models.section import Section
from app.models.course import Course

async def get_by_id(db: AsyncSession, professor_id: uuid.UUID) -> Optional[Professor]:
    result = await db.execute(select(Professor).where(Professor.id == professor_id))
    return result.scalar_one_or_none()


async def get_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[Professor]:
    result = await db.execute(select(Professor).where(Professor.user_id == user_id))
    return result.scalar_one_or_none()


async def get_all(
    db: AsyncSession,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Professor]:
    query = select(Professor)
    if department:
        query = query.where(Professor.department == department)
    query = query.order_by(Professor.last_name, Professor.first_name).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search(
    db: AsyncSession,
    query_str: str,
    skip: int = 0,
    limit: int = 50,
) -> list[Professor]:
    """Search professors by first or last name (case-insensitive)."""
    pattern = f"%{query_str.strip()}%"
    result = await db.execute(
        select(Professor)
        .where(
            or_(
                Professor.first_name.ilike(pattern),
                Professor.last_name.ilike(pattern),
            )
        )
        .order_by(Professor.last_name, Professor.first_name)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    first_name: str,
    last_name: str,
    department: Optional[str] = None,
    user_id: Optional[uuid.UUID] = None,
) -> Professor:
    professor = Professor(
        first_name=first_name,
        last_name=last_name,
        department=department,
        user_id=user_id,
    )
    db.add(professor)
    await db.flush()
    return professor


async def link_user(
    db: AsyncSession,
    professor: Professor,
    user_id: uuid.UUID,
) -> Professor:
    """Link an existing professor record to a user account after they register."""
    professor.user_id = user_id
    await db.flush()
    return professor


async def update(
    db: AsyncSession,
    professor: Professor,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    department: Optional[str] = None,
) -> Professor:
    if first_name is not None:
        professor.first_name = first_name
    if last_name is not None:
        professor.last_name = last_name
    if department is not None:
        professor.department = department
    await db.flush()
    return professor


async def delete(db: AsyncSession, professor: Professor) -> None:
    await db.delete(professor)
    await db.flush()
async def get_courses_by_professor(
    db: AsyncSession,
    professor_id: uuid.UUID,
) -> list[Course]:
    result = await db.execute(
        select(Course)
        .join(Section, Section.course_id == Course.id)
        .where(Section.professor_id == professor_id)
        .distinct()
        .order_by(Course.code)
    )
    return list(result.scalars().all())