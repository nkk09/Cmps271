from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.logger import setup_logger, get_logger
from app.api.health import router as health_router
from app.api.auth import router as auth_router

# Logging
setup_logger(level="DEBUG" if settings.ENV == "dev" else "INFO")
logger = get_logger(__name__)

app = FastAPI(title=settings.APP_NAME)

# CORS (needed when frontend calls backend endpoints with fetch + cookies)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session cookies (OAuth/login session)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=False,  # set True in production (https)
)

# Routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])

logger.info("Application startup complete")