"""
Violation routes — student reporting and admin moderation queue.
"""

import uuid
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dependencies import DBDep, CurrentStudent, AdminUser
from app.schemas import ViolationCreate, ViolationAdminUpdate, ViolationOut
from app import crud

router = APIRouter(tags=["violations"])


@router.post(
    "/reviews/{review_id}/violations",
    response_model=ViolationOut,
    status_code=status.HTTP_201_CREATED,
)
async def report_review_violation(
    review_id: uuid.UUID,
    body: ViolationCreate,
    db: DBDep,
    student: CurrentStudent,
):
    """Allow a student to report an approved review for moderation."""
    review = await crud.reviews.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved reviews can be reported.",
        )
    if review.student_id == student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot report your own review.",
        )

    existing = await crud.violations.get_existing_by_reporter(db, review_id, student.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already reported this review.",
        )

    violation = await crud.violations.create(
        db,
        review_id=review_id,
        reporter_student_id=student.id,
        violation_type=body.violation_type,
        severity=body.severity,
        reason=body.reason,
    )
    await db.commit()
    violation = await crud.violations.get_by_id(db, violation.id, load_relations=True)
    return ViolationOut.model_validate(violation)


@router.get("/violations", response_model=list[ViolationOut])
async def list_violations(
    db: DBDep,
    _: AdminUser,
    status_filter: Optional[Literal["open", "in_review", "resolved", "dismissed"]] = Query(default=None),
    severity: Optional[Literal["low", "medium", "high", "critical"]] = Query(default=None),
    violation_type: Optional[Literal[
        "spam",
        "harassment",
        "hate_speech",
        "misinformation",
        "personal_data",
        "other",
    ]] = Query(default=None),
    search: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Admin-only moderation queue with filtering by status, severity, type, and text search."""
    violations = await crud.violations.list_for_admin(
        db,
        status=status_filter,
        severity=severity,
        violation_type=violation_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return [ViolationOut.model_validate(v) for v in violations]


@router.get("/violations/{violation_id}", response_model=ViolationOut)
async def get_violation(
    violation_id: uuid.UUID,
    db: DBDep,
    _: AdminUser,
):
    """Get a single moderation case by id (admin only)."""
    violation = await crud.violations.get_by_id(db, violation_id, load_relations=True)
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")
    return ViolationOut.model_validate(violation)


@router.patch("/violations/{violation_id}", response_model=ViolationOut)
async def update_violation(
    violation_id: uuid.UUID,
    body: ViolationAdminUpdate,
    db: DBDep,
    admin: AdminUser,
):
    """Admin moderation action: triage, resolve, dismiss, add notes."""
    violation = await crud.violations.get_by_id(db, violation_id)
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")

    async def repair_status_constraint() -> bool:
        try:
            await db.rollback()
            await db.execute(
                text(
                    "ALTER TABLE violations DROP CONSTRAINT IF EXISTS ck_violation_status"
                )
            )
            await db.execute(
                text(
                    "ALTER TABLE violations ADD CONSTRAINT ck_violation_status CHECK (status IN ('open', 'in_review', 'resolved', 'dismissed'))"
                )
            )
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    async def perform_update() -> None:
        nonlocal violation
        violation = await crud.violations.update_for_admin(
            db,
            violation=violation,
            admin_user_id=admin.id,
            status=body.status,
            severity=body.severity,
            admin_notes=body.admin_notes,
        )
        await db.commit()

    try:
        await perform_update()
    except IntegrityError as exc:
        if "ck_violation_status" in str(exc) or "status" in str(exc):
            if await repair_status_constraint():
                try:
                    await perform_update()
                except IntegrityError as exc2:
                    await db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid violation update. Please ensure the status is one of open, in_review, resolved, or dismissed.",
                    ) from exc2
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to repair violation status constraint.",
                ) from exc
        else:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid violation update. Please ensure the status is one of open, in_review, resolved, or dismissed.",
            ) from exc

    violation = await crud.violations.get_by_id(db, violation_id, load_relations=True)
    return ViolationOut.model_validate(violation)
