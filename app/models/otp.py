"""
OTP (One-Time Password) model for email-based authentication.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class OTP(Base):
    """
    Stores one-time passwords for email verification.
    Each OTP is tied to an email and has an expiry time.
    """
    __tablename__ = "otps"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Attempt counter: increments on each verify failure
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<OTP(email={self.email}, expires_at={self.expires_at.isoformat()})>"
    
    @classmethod
    def is_expired(cls, otp: "OTP") -> bool:
        """Check if OTP has expired."""
        return datetime.utcnow() > otp.expires_at
    
    @classmethod
    def create(
        cls,
        session,
        email: str,
        code: str,
        expires_at: datetime,
    ) -> "OTP":
        """Create a new OTP record."""
        otp = cls(email=email.lower(), code=code, expires_at=expires_at)
        session.add(otp)
        session.commit()
        return otp
    
    @classmethod
    def get_latest_for_email(cls, session, email: str) -> "OTP | None":
        """Get the most recent non-expired OTP for given email."""
        return (
            session.query(cls)
            .filter(cls.email == email.lower())
            .filter(cls.expires_at > datetime.utcnow())
            .order_by(cls.created_at.desc())
            .first()
        )
    
    @classmethod
    def count_recent_for_email(cls, session, email: str, minutes: int = 60) -> int:
        """Count OTPs created for this email in the last N minutes."""
        cutoff = datetime.utcnow() - __import__("datetime").timedelta(minutes=minutes)
        return (
            session.query(cls)
            .filter(cls.email == email.lower())
            .filter(cls.created_at > cutoff)
            .count()
        )
    
    @classmethod
    def cleanup_expired(cls, session) -> int:
        """Delete all expired OTP records. Returns count deleted."""
        count = (
            session.query(cls)
            .filter(cls.expires_at <= datetime.utcnow())
            .delete()
        )
        session.commit()
        return count
