"""
User ORM model.
Authentication is email-based via OTP. The email is encrypted at rest;
a blind index is stored separately for lookups.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.core.encryption import encrypt_field, decrypt_field, blind_index


class User(Base):
    """
    Core authenticated user.
    - Email is encrypted (AES-256-GCM); query via email_index (HMAC blind index).
    - Personal profile lives in the linked Student or Professor record.
    - Roles are managed via the UserRole join table.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Encrypted email — never query this column directly, use email_index
    email_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    # HMAC-SHA256 blind index — use this for WHERE lookups
    email_index: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    # 'active' | 'suspended' | 'inactive'
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    professor: Mapped[Optional["Professor"]] = relationship("Professor", back_populates="user", uselist=False)
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user")
    assigned_violations: Mapped[list["Violation"]] = relationship(
        "Violation",
        foreign_keys="Violation.assigned_admin_id",
        back_populates="assigned_admin",
    )

    # ------------------------------------------------------------------
    # Email property — transparently encrypts/decrypts
    # ------------------------------------------------------------------

    @property
    def email(self) -> str:
        """Decrypt and return the stored email address."""
        return decrypt_field(self.email_encrypted)

    @classmethod
    def make(cls, email: str, **kwargs) -> "User":
        """
        Convenience constructor that handles encryption automatically.
        Usage: user = User.make(email="alice@uni.edu")
        """
        normalised = email.strip().lower()
        return cls(
            email_encrypted=encrypt_field(normalised),
            email_index=blind_index(normalised),
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email_index={self.email_index[:8]}…, status={self.status})>"