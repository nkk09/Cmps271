"""
Professor ORM model.
"""

import uuid
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Professor(Base):
    """
    Professor profile. Linked 1-to-1 with a User account (nullable — professors
    may exist in the system before they create an account).
    """
    __tablename__ = "professors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Nullable: professor record can be seeded before the professor registers
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="professor")
    sections: Mapped[list["Section"]] = relationship("Section", back_populates="professor")

    def __repr__(self) -> str:
        return f"<Professor(id={self.id}, name={self.first_name} {self.last_name})>"