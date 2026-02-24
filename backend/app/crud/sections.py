"""
CRUD operations for Section model.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.section import Section


async def get_by_id(
    db: AsyncSession,
    section_id: uuid.UUID,
    load_relations: bool = False,
) -> Optional[Section]:
    query = select(Section).where(Section.id == section_id)
    if load_relations:
        query = query.options(
            selectinload(Section.course),
            selectinload(Section.professor),
            selectinload(Section.semester),
        )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_course(
    db: AsyncSession,
    course_id: uuid.UUID,
    semester_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Section]:
    query = select(Section).where(Section.course_id == course_id)
    if semester_id:
        query = query.where(Section.semester_id == semester_id)
    query = query.options(
        selectinload(Section.course),
        selectinload(Section.professor),
        selectinload(Section.semester),
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_professor(
    db: AsyncSession,
    professor_id: uuid.UUID,
    semester_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Section]:
    query = select(Section).where(Section.professor_id == professor_id)
    if semester_id:
        query = query.where(Section.semester_id == semester_id)
    query = query.options(
        selectinload(Section.course),
        selectinload(Section.semester),
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_semester(
    db: AsyncSession,
    semester_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Section]:
    query = (
        select(Section)
        .where(Section.semester_id == semester_id)
        .options(
            selectinload(Section.course),
            selectinload(Section.professor),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    course_id: uuid.UUID,
    professor_id: uuid.UUID,
    semester_id: uuid.UUID,
    section_number: str,
    credits: Optional[int] = None,
    time: Optional[str] = None,
) -> Section:
    section = Section(
        course_id=course_id,
        professor_id=professor_id,
        semester_id=semester_id,
        section_number=section_number,
        credits=credits,
        time=time,
    )
    db.add(section)
    await db.flush()
    return section


async def update(
    db: AsyncSession,
    section: Section,
    professor_id: Optional[uuid.UUID] = None,
    credits: Optional[int] = None,
    time: Optional[str] = None,
) -> Section:
    if professor_id is not None:
        section.professor_id = professor_id
    if credits is not None:
        section.credits = credits
    if time is not None:
        section.time = time
    await db.flush()
    return section


async def delete(db: AsyncSession, section: Section) -> None:
    await db.delete(section)
    await db.flush()