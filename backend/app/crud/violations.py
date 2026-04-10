"""
CRUD operations for Violation model.
"""

import uuid
from datetime import datetime
from typing import Optional, Literal

from sqlalchemy import select, desc, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.student import Student
from app.models.violation import Violation

ViolationStatus = Literal["open", "in_review", "resolved", "dismissed"]
ViolationSeverity = Literal["low", "medium", "high", "critical"]
ViolationType = Literal[
    "spam",
    "harassment",
    "hate_speech",
    "misinformation",
    "personal_data",
    "other",
]


def _violation_review_options():
    from app.models.section import Section

    return [
        selectinload(Violation.review).options(
            selectinload(Review.student),
            selectinload(Review.section).options(
                selectinload(Section.course),
                selectinload(Section.professor),
                selectinload(Section.semester),
            ),
        ),
        selectinload(Violation.reported_by_student),
        selectinload(Violation.assigned_admin),
    ]


async def get_by_id(
    db: AsyncSession,
    violation_id: uuid.UUID,
    load_relations: bool = False,
) -> Optional[Violation]:
    query = select(Violation).where(Violation.id == violation_id)
    if load_relations:
        query = query.options(*_violation_review_options())
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_existing_by_reporter(
    db: AsyncSession,
    review_id: uuid.UUID,
    student_id: uuid.UUID,
) -> Optional[Violation]:
    result = await db.execute(
        select(Violation).where(
            Violation.review_id == review_id,
            Violation.reported_by_student_id == student_id,
        )
    )
    return result.scalar_one_or_none()


async def list_for_admin(
    db: AsyncSession,
    status: Optional[ViolationStatus] = None,
    severity: Optional[ViolationSeverity] = None,
    violation_type: Optional[ViolationType] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Violation]:
    query = (
        select(Violation)
        .options(*_violation_review_options())
        .order_by(desc(Violation.created_at))
    )

    if status:
        query = query.where(Violation.status == status)
    if severity:
        query = query.where(Violation.severity == severity)
    if violation_type:
        query = query.where(Violation.violation_type == violation_type)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = (
            query.join(Violation.review)
            .outerjoin(Violation.reported_by_student)
            .where(
                or_(
                    Review.content.ilike(search_pattern),
                    Student.username.ilike(search_pattern),
                )
            )
        )

    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    review_id: uuid.UUID,
    reporter_student_id: Optional[uuid.UUID],
    violation_type: ViolationType,
    severity: ViolationSeverity,
    reason: Optional[str],
) -> Violation:
    violation = Violation(
        review_id=review_id,
        reported_by_student_id=reporter_student_id,
        violation_type=violation_type,
        severity=severity,
        reason=reason,
        status="open",
    )
    db.add(violation)
    await db.flush()
    return violation


async def update_for_admin(
    db: AsyncSession,
    violation: Violation,
    admin_user_id: uuid.UUID,
    status: Optional[ViolationStatus] = None,
    severity: Optional[ViolationSeverity] = None,
    admin_notes: Optional[str] = None,
) -> Violation:
    violation.assigned_admin_id = admin_user_id

    if status is not None:
        violation.status = status
        if status in ("resolved", "dismissed"):
            violation.resolved_at = datetime.utcnow()
        else:
            violation.resolved_at = None

    if severity is not None:
        violation.severity = severity

    if admin_notes is not None:
        violation.admin_notes = admin_notes

    violation.updated_at = datetime.utcnow()
    await db.flush()
    return violation
