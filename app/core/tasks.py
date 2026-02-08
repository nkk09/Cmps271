"""
Background tasks and scheduled jobs.
"""

from app.core.database import SessionLocal
from app.core.logger import get_logger
from app.models.otp import OTP

logger = get_logger(__name__)


def cleanup_expired_otps() -> int:
    """Clean up expired OTP records from the database."""
    db = SessionLocal()
    try:
        count = OTP.cleanup_expired(db)
        if count > 0:
            logger.info(f"Cleaned up {count} expired OTP records")
        return count
    except Exception as e:
        logger.error(f"Failed to cleanup expired OTPs: {e}")
        return 0
    finally:
        db.close()
