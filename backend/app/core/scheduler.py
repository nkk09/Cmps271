"""
Optional scheduled background tasks using APScheduler.
Usage: import and call setup_scheduler() in main.py if APScheduler is installed.

Example:
    from app.core.scheduler import setup_scheduler
    
    @app.on_event("startup")
    def startup_event():
        init_db()
        setup_scheduler()
"""

from app.core.logger import get_logger
from app.core.tasks import cleanup_expired_otps

logger = get_logger(__name__)


def setup_scheduler():
    """
    Initialize the background scheduler for periodic maintenance tasks.
    This is optional and only required if APScheduler is installed.
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        scheduler = BackgroundScheduler()
        
        # Schedule OTP cleanup every 30 minutes
        scheduler.add_job(
            cleanup_expired_otps,
            "interval",
            minutes=30,
            id="cleanup_expired_otps",
            name="Clean up expired OTP records",
            replace_existing=True,
        )
        
        if not scheduler.running:
            scheduler.start()
            logger.info("Background scheduler started")
        
        return scheduler
        
    except ImportError:
        logger.warning("APScheduler not installed; skipping scheduled tasks. Install with: pip install apscheduler")
        return None
    except Exception as e:
        logger.error(f"Failed to setup scheduler: {e}")
        return None
