"""
Violation ORM model.
Stores moderation reports raised against reviews.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Violation(Base):
    """
    A moderation report on a review.
    Reported by students and triaged/resolved by admins.
    """

    __tablename__ = "violations"
    __table_args__ = (
        UniqueConstraint(
            "review_id",
            "reported_by_student_id",
            name="uq_violation_per_reporter_review",
        ),
        CheckConstraint(
            "violation_type IN ('spam', 'harassment', 'hate_speech', 'misinformation', 'personal_data', 'other')",
            name="ck_violation_type",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_violation_severity",
        ),
        CheckConstraint(
            "status IN ('open', 'in_review', 'resolved', 'dismissed')",
            name="ck_violation_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reported_by_student_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    violation_type: Mapped[str] = mapped_column(String(40), default="other", nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    review: Mapped["Review"] = relationship("Review", back_populates="violations")
    reported_by_student: Mapped[Optional["Student"]] = relationship(
        "Student",
        foreign_keys=[reported_by_student_id],
        back_populates="reported_violations",
    )
    assigned_admin: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_admin_id],
        back_populates="assigned_violations",
    )

    def __repr__(self) -> str:
        return f"<Violation(id={self.id}, review_id={self.review_id}, status={self.status})>"
