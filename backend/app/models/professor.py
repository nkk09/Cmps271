"""
Professor ORM model.
Stores professor information and their relationship to courses.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Professor(Base):
    """
    Professor model - stores professor information.
    Professors can teach multiple courses and sections.
    """
    __tablename__ = "professors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Professor identifiers
    # Note: In a real system, this should be unique per university system
    entra_oid: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Professor details
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    office: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status: 'active' or 'inactive'
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sections: Mapped[list["CourseSection"]] = relationship("CourseSection", back_populates="professor")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="professor", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Professor(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
