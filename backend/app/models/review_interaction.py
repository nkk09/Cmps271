"""
ReviewInteraction ORM model.
Stores user interactions (likes/dislikes) with reviews for smart review ranking.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ReviewInteraction(Base):
    """
    ReviewInteraction model - stores user interactions with reviews.
    Enables smart review ranking based on likes/dislikes.
    One interaction per user per review (can like or dislike, but not both).
    """
    __tablename__ = "review_interactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Interaction type
    interaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Values: 'like' or 'dislike'
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    review: Mapped["Review"] = relationship("Review", back_populates="interactions")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<ReviewInteraction(review_id={self.review_id}, user_id={self.user_id}, type={self.interaction_type})>"
