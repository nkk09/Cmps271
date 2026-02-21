"""
ModerationLog ORM model.
Tracks all admin moderation actions for transparency and audit purposes.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ModerationLog(Base):
    """
    ModerationLog model - tracks all admin moderation actions.
    Provides audit trail for transparency and accountability.
    """
    __tablename__ = "moderation_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    moderator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)  # User being moderated (if applicable)
    review_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reviews.id"), nullable=True, index=True)  # Review being moderated (if applicable)
    
    # Action details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Values: 'review_rejected', 'review_approved', 'review_edited', 'review_deleted',
    #         'user_suspended', 'user_activated', 'user_blocked', 'other'
    
    # Action reason/notes
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Additional details about the action
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)
    # Values: 'pending', 'completed', 'reversed', 'appealed'
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    moderator: Mapped["User"] = relationship("User", foreign_keys=[moderator_id])
    moderated_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    review: Mapped[Optional["Review"]] = relationship("Review")
    
    def __repr__(self) -> str:
        return f"<ModerationLog(id={self.id}, moderator_id={self.moderator_id}, action_type={self.action_type})>"
