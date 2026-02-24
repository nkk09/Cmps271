"""
CRUD operations for OTP model.
Business logic: generation, verification, rate limiting, cleanup.
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp import OTP
from app.core.encryption import blind_index, hash_otp, verify_otp

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5
OTP_RATE_LIMIT_COUNT = 5       # max OTPs per email per window
OTP_RATE_LIMIT_MINUTES = 60


def _generate_code() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(10 ** OTP_LENGTH)).zfill(OTP_LENGTH)


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

async def get_latest_for_email(db: AsyncSession, email: str) -> Optional[OTP]:
    """Get the most recent non-expired, unverified OTP for an email."""
    result = await db.execute(
        select(OTP)
        .where(
            OTP.email_index == blind_index(email),
            OTP.expires_at > datetime.utcnow(),
            OTP.verified_at.is_(None),
        )
        .order_by(OTP.created_at.desc())
    )
    return result.scalar_one_or_none()


async def count_recent_for_email(
    db: AsyncSession,
    email: str,
    minutes: int = OTP_RATE_LIMIT_MINUTES,
) -> int:
    """Count OTPs issued to this email in the last N minutes."""
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    result = await db.execute(
        select(func.count(OTP.id)).where(
            OTP.email_index == blind_index(email),
            OTP.created_at > cutoff,
        )
    )
    return result.scalar_one()


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

async def create(
    db: AsyncSession,
    email: str,
    user_id: Optional[uuid.UUID] = None,
) -> tuple[OTP, str]:
    """
    Create a new OTP for the given email.
    Returns (otp_record, plain_code) — plain_code must be sent to the user
    and never stored. The record stores only the hash.
    """
    plain_code = _generate_code()
    otp = OTP(
        user_id=user_id,
        email_encrypted=__import__('app.core.encryption', fromlist=['encrypt_field']).encrypt_field(email.strip().lower()),
        email_index=blind_index(email),
        code_hash=hash_otp(plain_code),
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.add(otp)
    await db.flush()
    return otp, plain_code


async def verify(
    db: AsyncSession,
    email: str,
    plain_code: str,
) -> tuple[bool, Optional[OTP], Optional[str]]:
    """
    Verify a plain OTP code for an email.

    Returns (success, otp_record, error_message).
    On success, marks the OTP as verified.
    On failure, increments the attempt counter.

    Possible error strings:
        'not_found'   — no active OTP for this email
        'expired'     — OTP has passed its expiry
        'max_attempts'— too many failed attempts
        'invalid_code'— code does not match
    """
    otp = await get_latest_for_email(db, email)

    if otp is None:
        return False, None, "not_found"

    if otp.is_expired:
        return False, otp, "expired"

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        return False, otp, "max_attempts"

    if not verify_otp(otp.code_hash, plain_code):
        otp.attempts += 1
        await db.flush()
        return False, otp, "invalid_code"

    # Success
    otp.verified_at = datetime.utcnow()
    await db.flush()
    return True, otp, None


async def is_rate_limited(db: AsyncSession, email: str) -> bool:
    """Return True if this email has hit the OTP request rate limit."""
    count = await count_recent_for_email(db, email)
    return count >= OTP_RATE_LIMIT_COUNT


async def cleanup_expired(db: AsyncSession) -> int:
    """Delete all expired OTP records. Returns count deleted."""
    result = await db.execute(
        select(OTP).where(OTP.expires_at <= datetime.utcnow())
    )
    expired = result.scalars().all()
    for otp in expired:
        await db.delete(otp)
    await db.flush()
    return len(expired)
