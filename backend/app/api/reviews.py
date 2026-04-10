"""
Reviews routes — submit, edit, delete, like/dislike.
"""

import uuid
from typing import Literal

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status, Depends

from app.dependencies import DBDep, CurrentUserOptional, CurrentStudent, AdminUser
from app.schemas import ReviewCreate, ReviewUpdate, ReviewOut, ReviewStatusUpdate, InteractionResponse
from app import crud

router = APIRouter(tags=["reviews"])


# ---------------------------------------------------------------------------
# Muted / Blocked enforcement
# ---------------------------------------------------------------------------

def enforce_not_muted_or_blocked(student: CurrentStudent):
    """
    Blocks review posting/editing/deleting if the user is blocked or muted.
    """
    user = getattr(student, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="No user linked to student")

    if getattr(user, "is_blocked", False):
        raise HTTPException(status_code=403, detail="User is blocked")

    muted_until = getattr(user, "muted_until", None)
    if muted_until and muted_until > datetime.utcnow():
        raise HTTPException(
            status_code=403,
            detail=f"User is muted until {muted_until.isoformat()}",
        )


# ---------------------------------------------------------------------------
# Reviews on a section
# ---------------------------------------------------------------------------

@router.get("/sections/{section_id}/reviews", response_model=list[ReviewOut])
async def get_section_reviews(
    section_id: uuid.UUID,
    db: DBDep,
    user: CurrentUserOptional,
    sort_by: Literal["newest", "top_rated", "most_liked"] = Query(default="newest"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
):
    section = await crud.sections.get_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    reviews = await crud.reviews.get_by_section(
        db, section_id, sort_by=sort_by, skip=skip, limit=limit
    )
    return await _annotate_interactions(db, reviews, user)


@router.post("/sections/{section_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(
    section_id: uuid.UUID,
    body: ReviewCreate,
    db: DBDep,
    student: CurrentStudent,
    _=Depends(enforce_not_muted_or_blocked),
):
    section = await crud.sections.get_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    already_reviewed = await crud.reviews.student_has_reviewed_section(db, student.id, section_id)
    if already_reviewed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this section.",
        )

    review = await crud.reviews.create(
        db,
        student_id=student.id,
        section_id=section_id,
        content=body.content,
        rating=body.rating,
    )
    await db.commit()
    await db.refresh(review, attribute_names=["student", "section"])
    await db.refresh(review.section, attribute_names=["course", "professor", "semester"])
    return ReviewOut.model_validate(review)


# ---------------------------------------------------------------------------
# Reviews on a professor
# ---------------------------------------------------------------------------

@router.get("/professors/{professor_id}/reviews", response_model=list[ReviewOut])
async def get_professor_reviews(
    professor_id: uuid.UUID,
    db: DBDep,
    user: CurrentUserOptional,
    sort_by: Literal["newest", "top_rated", "most_liked"] = Query(default="newest"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
):
    professor = await crud.professors.get_by_id(db, professor_id)
    if not professor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")

    reviews = await crud.reviews.get_by_professor(
        db, professor_id, sort_by=sort_by, skip=skip, limit=limit
    )
    return await _annotate_interactions(db, reviews, user)


# ---------------------------------------------------------------------------
# Admin review moderation
# ---------------------------------------------------------------------------

@router.get("/reviews/pending", response_model=list[ReviewOut])
async def list_pending_reviews(
    db: DBDep,
    _: AdminUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Admin-only: list all reviews awaiting approval."""
    reviews = await crud.reviews.get_pending(db, skip=skip, limit=limit)
    return [ReviewOut.model_validate(r) for r in reviews]


@router.patch("/reviews/{review_id}/status", response_model=ReviewOut)
async def update_review_status(
    review_id: uuid.UUID,
    body: ReviewStatusUpdate,
    db: DBDep,
    _: AdminUser,
):
    """Admin-only: approve or reject a pending review."""
    review = await crud.reviews.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    review = await crud.reviews.update_status(db, review, body.status)
    await db.commit()
    await db.refresh(review, attribute_names=["student", "section"])
    if review.section is not None:
        await db.refresh(review.section, attribute_names=["course", "professor", "semester"])
    return ReviewOut.model_validate(review)


# ---------------------------------------------------------------------------
# Individual review operations
# ---------------------------------------------------------------------------

@router.patch("/reviews/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: uuid.UUID,
    body: ReviewUpdate,
    db: DBDep,
    student: CurrentStudent,
    _=Depends(enforce_not_muted_or_blocked),
):
    review = await crud.reviews.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.student_id != student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your review")

    if body.content is not None or body.rating is not None:
        review = await crud.reviews.update_content(
            db,
            review,
            content=body.content or review.content,
            rating=body.rating or review.rating,
        )
    await db.commit()
    await db.refresh(review, attribute_names=["student", "section"])
    if review.section is not None:
        await db.refresh(review.section, attribute_names=["course", "professor", "semester"])
    return ReviewOut.model_validate(review)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: uuid.UUID,
    db: DBDep,
    student: CurrentStudent,
    _=Depends(enforce_not_muted_or_blocked),
):
    review = await crud.reviews.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.student_id != student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your review")

    await crud.reviews.delete(db, review)
    await db.commit()


# ---------------------------------------------------------------------------
# Like / Dislike
# ---------------------------------------------------------------------------

@router.post("/reviews/{review_id}/like", response_model=InteractionResponse)
async def like_review(review_id: uuid.UUID, db: DBDep, student: CurrentStudent):
    return await _interact(db, review_id, student.id, "like")


@router.post("/reviews/{review_id}/dislike", response_model=InteractionResponse)
async def dislike_review(review_id: uuid.UUID, db: DBDep, student: CurrentStudent):
    return await _interact(db, review_id, student.id, "dislike")


@router.delete("/reviews/{review_id}/interaction", status_code=status.HTTP_204_NO_CONTENT)
async def remove_interaction(review_id: uuid.UUID, db: DBDep, student: CurrentStudent):
    review = await crud.reviews.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    await crud.review_interactions.remove(db, review=review, student_id=student.id)
    await db.commit()


# ---------------------------------------------------------------------------
# My reviews
# ---------------------------------------------------------------------------

@router.get("/users/me/reviews", response_model=list[ReviewOut])
async def get_my_reviews(
    db: DBDep,
    student: CurrentStudent,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
):
    reviews = await crud.reviews.get_by_student(db, student.id, skip=skip, limit=limit)
    return [ReviewOut.model_validate(r) for r in reviews]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _interact(db, review_id: uuid.UUID, student_id: uuid.UUID, interaction_type: str):
    review = await crud.reviews.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot interact with a non-approved review")
    if review.student_id == student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot like or dislike your own review")

    await crud.review_interactions.upsert(
        db, review=review, student_id=student_id, interaction_type=interaction_type
    )
    await db.commit()
    await db.refresh(review)

    return InteractionResponse(
        review_id=review.id,
        interaction_type=interaction_type,
        likes_count=review.likes_count,
        dislikes_count=review.dislikes_count,
    )


async def _annotate_interactions(db, reviews, user) -> list[ReviewOut]:
    if not reviews:
        return []

    interaction_map = {}

    if user:
        student = await crud.students.get_by_user_id(db, user.id)
        if student:
            review_ids = [r.id for r in reviews]
            interaction_map = await crud.review_interactions.get_student_interactions(
                db, student.id, review_ids
            )

    result = []
    for review in reviews:
        out = ReviewOut.model_validate(review)
        out.my_interaction = interaction_map.get(review.id)
        result.append(out)

    return result