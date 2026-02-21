"""
Review ORM model.
Stores reviews of courses and professors by users.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Review(Base):
    """
    Review model - stores reviews of courses and professors.
    Each review is anonymous and tied to a user, course, and professor.
    Users can like/dislike reviews to affect their visibility.
    """
    __tablename__ = "reviews"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    professor_id: Mapped[int] = mapped_column(ForeignKey("professors.id"), nullable=False, index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("course_sections.id"), nullable=True, index=True)
    
    # Review content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Rating (on a scale of 1-5)
    rating: Mapped[float] = mapped_column(Float, nullable=False)  # 1.0 to 5.0
    
    # Review attributes (tags/categories)
    # Format: comma-separated values like "difficulty,workload,teaching_style"
    attributes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Moderation status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    # Status values: 'pending' (awaiting moderation), 'approved', 'flagged', 'rejected'
    
    # Moderation details
    moderator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    moderation_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    moderated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Visibility metrics
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dislikes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Soft delete timestamp
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    course: Mapped["Course"] = relationship("Course", back_populates="reviews")
    professor: Mapped["Professor"] = relationship("Professor", back_populates="reviews")
    section: Mapped[Optional["CourseSection"]] = relationship("CourseSection", back_populates="reviews")
    moderator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[moderator_id])
    interactions: Mapped[list["ReviewInteraction"]] = relationship("ReviewInteraction", back_populates="review", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, course_id={self.course_id}, professor_id={self.professor_id}, rating={self.rating})>"
    
    @property
    def is_active(self) -> bool:
        """Check if review is not deleted and is approved."""
        return self.deleted_at is None and self.status == "approved"
    
    @property
    def net_rating(self) -> int:
        """Calculate net rating (likes - dislikes)."""
        return self.likes_count - self.dislikes_count
