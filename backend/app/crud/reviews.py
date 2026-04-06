"""
CRUD operations for Review model.
"""

import uuid
from typing import Optional, Literal
from datetime import datetime

from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review

ReviewStatus = Literal["pending", "approved", "rejected"]
SortBy = Literal["newest", "top_rated", "most_liked"]


async def get_by_id(
    db: AsyncSession,
    review_id: uuid.UUID,
    load_relations: bool = False,
) -> Optional[Review]:
    query = select(Review).where(Review.id == review_id)
    if load_relations:
        query = query.options(
            selectinload(Review.student),
            selectinload(Review.section),
        )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_section(
    db: AsyncSession,
    section_id: uuid.UUID,
    status: ReviewStatus = "approved",
    sort_by: SortBy = "newest",
    skip: int = 0,
    limit: int = 20,
) -> list[Review]:
    query = (
        select(Review)
        .where(
            Review.section_id == section_id,
            Review.status == status,
        )
        .options(
            selectinload(Review.student),
            selectinload(Review.section).selectinload(Section.course),
            selectinload(Review.section).selectinload(Section.professor),
            selectinload(Review.section).selectinload(Section.semester),
        )
    )
    query = _apply_sort(query, sort_by)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_professor(
    db: AsyncSession,
    professor_id: uuid.UUID,
    status: ReviewStatus = "approved",
    sort_by: SortBy = "newest",
    skip: int = 0,
    limit: int = 20,
) -> list[Review]:
    """Get all reviews for any section taught by this professor."""
    from app.models.section import Section
    query = (
        select(Review)
        .join(Section, Review.section_id == Section.id)
        .where(
            Section.professor_id == professor_id,
            Review.status == status,
        )
        .options(
            selectinload(Review.student),
            selectinload(Review.section).selectinload(Section.course),
            selectinload(Review.section).selectinload(Section.professor),
            selectinload(Review.section).selectinload(Section.semester),
        )
    )
    query = _apply_sort(query, sort_by)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_course(
    db: AsyncSession,
    course_id: uuid.UUID,
    status: ReviewStatus = "approved",
    sort_by: SortBy = "newest",
    skip: int = 0,
    limit: int = 20,
) -> list[Review]:
    """Get all reviews for any section of this course."""
    from app.models.section import Section
    query = (
        select(Review)
        .join(Section, Review.section_id == Section.id)
        .where(
            Section.course_id == course_id,
            Review.status == status,
        )
        .options(
            selectinload(Review.student),
            selectinload(Review.section).selectinload(Section.course),
            selectinload(Review.section).selectinload(Section.professor),
            selectinload(Review.section).selectinload(Section.semester),
        )
    )
    query = _apply_sort(query, sort_by)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_student(
    db: AsyncSession,
    student_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> list[Review]:
    """Get all reviews written by a student (any status — for the student's own view)."""
    result = await db.execute(
        select(Review)
        .where(Review.student_id == student_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_pending(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> list[Review]:
    """Get reviews awaiting moderation — for admin/moderator use."""
    result = await db.execute(
        select(Review)
        .where(Review.status == "pending")
        .order_by(Review.created_at)  # oldest first — FIFO moderation queue
        .options(selectinload(Review.student), selectinload(Review.section))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_average_rating_for_section(
    db: AsyncSession,
    section_id: uuid.UUID,
) -> Optional[float]:
    result = await db.execute(
        select(func.avg(Review.rating)).where(
            Review.section_id == section_id,
            Review.status == "approved",
        )
    )
    return result.scalar_one_or_none()


async def get_average_rating_for_professor(
    db: AsyncSession,
    professor_id: uuid.UUID,
) -> Optional[float]:
    from app.models.section import Section
    result = await db.execute(
        select(func.avg(Review.rating))
        .join(Section, Review.section_id == Section.id)
        .where(
            Section.professor_id == professor_id,
            Review.status == "approved",
        )
    )
    return result.scalar_one_or_none()


async def student_has_reviewed_section(
    db: AsyncSession,
    student_id: uuid.UUID,
    section_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        select(Review.id).where(
            Review.student_id == student_id,
            Review.section_id == section_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def create(
    db: AsyncSession,
    student_id: uuid.UUID,
    section_id: uuid.UUID,
    content: str,
    rating: float,
) -> Review:
    review = Review(
        student_id=student_id,
        section_id=section_id,
        content=content,
        rating=rating,
        status="pending",
    )
    db.add(review)
    await db.flush()
    return review


async def update_status(
    db: AsyncSession,
    review: Review,
    status: ReviewStatus,
) -> Review:
    review.status = status
    review.updated_at = datetime.utcnow()
    await db.flush()
    return review


async def update_content(
    db: AsyncSession,
    review: Review,
    content: str,
    rating: float,
) -> Review:
    """Student editing their own review — goes back to pending for re-approval."""
    review.content = content
    review.rating = rating
    review.status = "pending"
    review.updated_at = datetime.utcnow()
    await db.flush()
    return review


async def increment_likes(db: AsyncSession, review: Review) -> Review:
    review.likes_count += 1
    await db.flush()
    return review


async def decrement_likes(db: AsyncSession, review: Review) -> Review:
    review.likes_count = max(0, review.likes_count - 1)
    await db.flush()
    return review


async def increment_dislikes(db: AsyncSession, review: Review) -> Review:
    review.dislikes_count += 1
    await db.flush()
    return review


async def decrement_dislikes(db: AsyncSession, review: Review) -> Review:
    review.dislikes_count = max(0, review.dislikes_count - 1)
    await db.flush()
    return review


async def delete(db: AsyncSession, review: Review) -> None:
    await db.delete(review)
    await db.flush()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_sort(query, sort_by: SortBy):
    if sort_by == "newest":
        return query.order_by(desc(Review.created_at))
    elif sort_by == "top_rated":
        return query.order_by(desc(Review.rating), desc(Review.created_at))
    elif sort_by == "most_liked":
        return query.order_by(
            desc(Review.likes_count - Review.dislikes_count),
            desc(Review.created_at),
        )
    return query
