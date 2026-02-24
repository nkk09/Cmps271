"""
Course ORM model.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.db.base import Base


class Course(Base):
    """
    A course offered by the university (e.g. CS101 - Intro to Programming).
    A course can have many sections across different semesters and professors.
    """
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # e.g. "CS101", "MATH201"
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Stored as a PostgreSQL text array, e.g. ["Writing Intensive", "Lab"]
    attributes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(100)), nullable=True)

    # Relationships
    sections: Mapped[list["Section"]] = relationship("Section", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Course(code={self.code}, title={self.title})>"