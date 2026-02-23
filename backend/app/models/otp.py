"""
OTP (One-Time Password) ORM model for email-based authentication.

Security design:
  - Email is encrypted at rest (AES-256-GCM) and searchable via an HMAC blind index.
  - OTP code is hashed with argon2id — never stored in plaintext.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.core.encryption import encrypt_field, decrypt_field, blind_index, hash_otp, verify_otp


class OTP(Base):
    """
    One-time password record tied to an email address.

    Columns:
        email_encrypted  — AES-256-GCM ciphertext of the normalised email
        email_index      — HMAC-SHA256 blind index; used for WHERE lookups
        code_hash        — argon2id hash of the 6-digit code
        attempts         — failed verification counter (lock out after N attempts)
        expires_at       — hard expiry timestamp
        verified_at      — set when successfully verified (makes OTP single-use)
    """
    __tablename__ = "otps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Optional link to an existing user (null for new registrations)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Encrypted email — decrypt via the `email` property
    email_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    # Deterministic HMAC index — query with blind_index(user_input)
    email_index: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Argon2id hash — never the raw code
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def email(self) -> str:
        """Decrypt and return the stored email address."""
        return decrypt_field(self.email_encrypted)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None

    def verify_code(self, code: str) -> bool:
        """Check a plain code against the stored hash."""
        return verify_otp(self.code_hash, code)

    # ------------------------------------------------------------------
    # Class-level helpers (thin wrappers — business logic lives in CRUD)
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        session: Session,
        email: str,
        code: str,
        expires_in_minutes: int = 10,
        user_id: Optional[uuid.UUID] = None,
    ) -> "OTP":
        """
        Create, persist, and return a new OTP record.
        The plain `code` is hashed immediately; only the hash is stored.
        """
        otp = cls(
            user_id=user_id,
            email_encrypted=encrypt_field(email.strip().lower()),
            email_index=blind_index(email),
            code_hash=hash_otp(code),
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        )
        session.add(otp)
        session.flush()  # get the id without committing — let caller manage the transaction
        return otp

    @classmethod
    def get_latest_for_email(cls, session: Session, email: str) -> Optional["OTP"]:
        """Return the most recent non-expired, unverified OTP for the given email."""
        return (
            session.query(cls)
            .filter(
                cls.email_index == blind_index(email),
                cls.expires_at > datetime.utcnow(),
                cls.verified_at.is_(None),
            )
            .order_by(cls.created_at.desc())
            .first()
        )

    @classmethod
    def count_recent_for_email(cls, session: Session, email: str, minutes: int = 60) -> int:
        """Count how many OTPs were requested for this email in the last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            session.query(cls)
            .filter(
                cls.email_index == blind_index(email),
                cls.created_at > cutoff,
            )
            .count()
        )

    @classmethod
    def cleanup_expired(cls, session: Session) -> int:
        """Delete all expired OTP records. Returns the number deleted."""
        count = (
            session.query(cls)
            .filter(cls.expires_at <= datetime.utcnow())
            .delete(synchronize_session=False)
        )
        session.flush()
        return count

    def __repr__(self) -> str:
        return f"<OTP(id={self.id}, email_index={self.email_index[:8]}…, expires_at={self.expires_at.isoformat()})>"