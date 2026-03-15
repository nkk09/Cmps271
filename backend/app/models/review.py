"""
Review ORM model.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Review(Base):
    """
    An anonymous review of a course section by a student.
    Moderated via status field before being publicly visible.
    Likes/dislikes are tracked in ReviewInteraction and denormalised here for
    fast sorting without aggregation queries.
    """
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1.0 AND rating <= 5.0", name="ck_review_rating_range"),
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_review_status"),
        CheckConstraint("likes_count >= 0", name="ck_review_likes_non_negative"),
        CheckConstraint("dislikes_count >= 0", name="ck_review_dislikes_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Nullable: review remains even if a section is deleted (historical record)
    section_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id", ondelete="SET NULL"), nullable=True, index=True
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)  # 1.0–5.0

    # Moderation status: 'pending' → 'approved' | 'rejected'
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)

    # Denormalised counters — kept in sync by CRUD layer when interactions change
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dislikes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="reviews")
    section: Mapped[Optional["Section"]] = relationship("Section", back_populates="reviews")
    interactions: Mapped[list["ReviewInteraction"]] = relationship(
        "ReviewInteraction", back_populates="review", cascade="all, delete-orphan"
    )
    violations: Mapped[list["Violation"]] = relationship(
        "Violation", back_populates="review", cascade="all, delete-orphan"
    )

    @property
    def net_score(self) -> int:
        """Net interaction score (likes − dislikes). Used for smart ranking."""
        return self.likes_count - self.dislikes_count

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, student_id={self.student_id}, rating={self.rating})>"