"""
Semester ORM model.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Semester(Base):
    """
    An academic semester (e.g. Fall 2024, Spring 2025).
    """
    __tablename__ = "semesters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Human-readable label, e.g. "Fall 2024"
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    starts_on: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_on: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    sections: Mapped[list["Section"]] = relationship("Section", back_populates="semester")

    def __repr__(self) -> str:
        return f"<Semester(name={self.name}, starts_on={self.starts_on.date()})>"