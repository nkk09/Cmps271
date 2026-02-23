"""
Section ORM model.
A specific offering of a course: one professor, one semester, one section number.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Section(Base):
    """
    A section ties a Course + Professor + Semester together.
    One course can have many sections per semester (e.g. CS101-001, CS101-002).
    """
    __tablename__ = "sections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    professor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("professors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("semesters.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # e.g. "001", "002", "H01" (honors)
    section_number: Mapped[str] = mapped_column(String(10), nullable=False)
    credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # e.g. "MWF 10:00-10:50 AM"
    time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="sections")
    professor: Mapped["Professor"] = relationship("Professor", back_populates="sections")
    semester: Mapped["Semester"] = relationship("Semester", back_populates="sections")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Section(course_id={self.course_id}, section_number={self.section_number})>"