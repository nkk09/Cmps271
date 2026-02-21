"""
CourseSection ORM model.
Represents a specific section of a course taught by a professor in a semester.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CourseSection(Base):
    """
    CourseSection model - represents a specific section of a course.
    Links a course to a professor for a specific semester.
    """
    __tablename__ = "course_sections"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    professor_id: Mapped[int] = mapped_column(ForeignKey("professors.id"), nullable=False, index=True)
    
    # Section details
    section_number: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., "01", "02", "L01"
    semester: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # e.g., "Fall2024", "Spring2025"
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # e.g., 2024, 2025
    
    # Section specifics
    time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "MWF 10:00-11:00"
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Room 201"
    credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status: 'active', 'archived', 'cancelled'
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="sections")
    professor: Mapped["Professor"] = relationship("Professor", back_populates="sections")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<CourseSection(id={self.id}, course_id={self.course_id}, professor_id={self.professor_id}, semester={self.semester})>"
    
    @property
    def identifier(self) -> str:
        """Return section identifier like 'CMPS271-01-Fall2024'"""
        return f"{self.course.course_number}-{self.section_number}-{self.semester}"
