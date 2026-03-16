"""
CRUD operations for ReviewInteraction model.

Handles like/dislike interactions on reviews.
Always call these instead of modifying Review.likes_count directly —
these functions keep the denormalised counters in sync automatically.
"""

import uuid
from typing import Optional, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review_interaction import ReviewInteraction
from app.models.review import Review

InteractionType = Literal["like", "dislike"]


async def get(
    db: AsyncSession,
    review_id: uuid.UUID,
    student_id: uuid.UUID,
) -> Optional[ReviewInteraction]:
    result = await db.execute(
        select(ReviewInteraction).where(
            ReviewInteraction.review_id == review_id,
            ReviewInteraction.student_id == student_id,
        )
    )
    return result.scalar_one_or_none()


async def upsert(
    db: AsyncSession,
    review: Review,
    student_id: uuid.UUID,
    interaction_type: InteractionType,
) -> ReviewInteraction:
    """
    Create or update a like/dislike interaction.
    Automatically syncs the denormalised counters on Review.

    - If no existing interaction: create it and increment the right counter.
    - If same type already exists: no-op (idempotent).
    - If opposite type exists: switch it and update both counters.
    """
    existing = await get(db, review.id, student_id)

    if existing is None:
        # New interaction
        interaction = ReviewInteraction(
            review_id=review.id,
            student_id=student_id,
            interaction_type=interaction_type,
        )
        db.add(interaction)
        _increment(review, interaction_type)
        await db.flush()
        return interaction

    if existing.interaction_type == interaction_type:
        # Already the same — idempotent, nothing to do
        return existing

    # Switching from one type to the other
    _decrement(review, existing.interaction_type)
    _increment(review, interaction_type)
    existing.interaction_type = interaction_type
    await db.flush()
    return existing


async def remove(
    db: AsyncSession,
    review: Review,
    student_id: uuid.UUID,
) -> bool:
    """
    Remove a student's interaction from a review.
    Decrements the appropriate counter.
    Returns True if an interaction was removed, False if none existed.
    """
    existing = await get(db, review.id, student_id)
    if existing is None:
        return False

    _decrement(review, existing.interaction_type)
    await db.delete(existing)
    await db.flush()
    return True


async def get_student_interactions(
    db: AsyncSession,
    student_id: uuid.UUID,
    review_ids: list[uuid.UUID],
) -> dict[uuid.UUID, InteractionType]:
    """
    For a list of review IDs, return a dict of {review_id: interaction_type}
    for the given student. Reviews with no interaction are omitted.
    Useful for annotating a feed of reviews with the current student's votes.
    """
    if not review_ids:
        return {}
    result = await db.execute(
        select(ReviewInteraction).where(
            ReviewInteraction.student_id == student_id,
            ReviewInteraction.review_id.in_(review_ids),
        )
    )
    return {i.review_id: i.interaction_type for i in result.scalars().all()}


# ---------------------------------------------------------------------------
# Private counter helpers — always go through upsert/remove, never directly
# ---------------------------------------------------------------------------

def _increment(review: Review, interaction_type: InteractionType) -> None:
    if interaction_type == "like":
        review.likes_count += 1
    else:
        review.dislikes_count += 1


def _decrement(review: Review, interaction_type: InteractionType) -> None:
    if interaction_type == "like":
        review.likes_count = max(0, review.likes_count - 1)
    else:
        review.dislikes_count = max(0, review.dislikes_count - 1)
