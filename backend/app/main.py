from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.logger import setup_logger, get_logger
from app.core.database import init_db
from app.core.tasks import cleanup_expired_otps
from app.api.health import router as health_router
from app.api.auth import router as auth_router

setup_logger(level="DEBUG" if settings.ENV == "dev" else "INFO")
logger = get_logger(__name__)

app = FastAPI(title=settings.APP_NAME)

# CORS (allow frontend dev servers on 5173 and 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Initialize database and clean up expired OTPs on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        # Clean up any expired OTP records
        cleanup_expired_otps()
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


logger.info("Application startup complete")
