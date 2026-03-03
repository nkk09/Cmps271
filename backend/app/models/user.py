"""
User ORM model.
Authentication is email-based via OTP. The email is encrypted at rest;
a blind index is stored separately for lookups.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.core.encryption import encrypt_field, decrypt_field, blind_index


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ✅ Admin moderation fields
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    muted_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Encrypted email
    email_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    email_index: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    professor: Mapped[Optional["Professor"]] = relationship("Professor", back_populates="user", uselist=False)
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user")

    @property
    def email(self) -> str:
        return decrypt_field(self.email_encrypted)

    @classmethod
    def make(cls, email: str, **kwargs) -> "User":
        normalised = email.strip().lower()
        return cls(
            email_encrypted=encrypt_field(normalised),
            email_index=blind_index(normalised),
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email_index={self.email_index[:8]}…, status={self.status})>"