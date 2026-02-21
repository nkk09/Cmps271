"""
Course ORM model.
Stores course information including course number, name, department, etc.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Course(Base):
    """
    Course model - stores course information.
    Multiple sections can exist for the same course.
    """
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Course identifiers
    course_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # e.g., "CMPS 271"
    course_name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "Data Structures"
    
    # Course details
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "Computer Science"
    credit_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sections: Mapped[list["CourseSection"]] = relationship("CourseSection", back_populates="course", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Course(id={self.id}, course_number={self.course_number}, course_name={self.course_name})>"
