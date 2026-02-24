"""
ReviewInteraction ORM model.
One record per (user, review) pair — a user can like OR dislike a review, not both.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class ReviewInteraction(Base):
    """
    Tracks per-user like/dislike interactions on reviews.
    The unique constraint on (review_id, user_id) prevents duplicate interactions.
    When an interaction is created or changed, the CRUD layer updates
    Review.likes_count / Review.dislikes_count accordingly.
    """
    __tablename__ = "review_interactions"
    __table_args__ = (
        UniqueConstraint("review_id", "student_id", name="uq_review_interaction_per_student"),
        CheckConstraint("interaction_type IN ('like', 'dislike')", name="ck_interaction_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 'like' | 'dislike'
    interaction_type: Mapped[str] = mapped_column(String(10), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    review: Mapped["Review"] = relationship("Review", back_populates="interactions")
    student: Mapped["Student"] = relationship("Student", back_populates="review_interactions")

    def __repr__(self) -> str:
        return f"<ReviewInteraction(review_id={self.review_id}, student_id={self.student_id}, type={self.interaction_type})>"