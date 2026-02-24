"""
Background tasks and scheduled jobs.
"""

import asyncio
from app.db.base import AsyncSessionLocal
from app.core.logger import get_logger
from app import crud

logger = get_logger(__name__)


async def cleanup_expired_otps() -> int:
    """Clean up expired OTP records from the database."""
    async with AsyncSessionLocal() as db:
        try:
            count = await crud.otps.cleanup_expired(db)
            await db.commit()
            if count > 0:
                logger.info(f"Cleaned up {count} expired OTP records")
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to cleanup expired OTPs: {e}")
            return 0


async def run_periodically(interval_seconds: int):
    """Run OTP cleanup on a schedule while the app is alive."""
    while True:
        await cleanup_expired_otps()
        await asyncio.sleep(interval_seconds)