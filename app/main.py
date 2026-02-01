from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logger, get_logger
from app.api.health import router as health_router
from app.api.auth import router as auth_router

setup_logger(level="DEBUG" if settings.ENV == "dev" else "INFO")
logger = get_logger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])

logger.info("Application startup complete")
