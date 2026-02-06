from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.logger import setup_logger, get_logger
from app.core.database import init_db
from app.api.health import router as health_router
from app.api.auth import router as auth_router

setup_logger(level="DEBUG" if settings.ENV == "dev" else "INFO")
logger = get_logger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=False,  # set True in production
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


logger.info("Application startup complete")
