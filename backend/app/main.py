"""
FastAPI application entry point.
"""

import time
import uuid

from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import get_logger, setup_logger

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.courses import (
    courses_router,
    professors_router,
    sections_router,
    semesters_router,
)
from app.api.reviews import router as reviews_router
from app.api.violations import router as violations_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "dev" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_logging() -> None:
    setup_logger("DEBUG" if settings.ENV == "dev" else "INFO")
    logger.info(
        "Application startup: app=%s env=%s version=%s",
        settings.APP_NAME,
        settings.ENV,
        app.version,
    )


@app.on_event("shutdown")
async def shutdown_logging() -> None:
    logger.info("Application shutdown: app=%s env=%s", settings.APP_NAME, settings.ENV)


def _get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for", "")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id

    path = request.url.path
    method = request.method
    client_ip = _get_client_ip(request)
    start = time.perf_counter()

    logger.info(
        "Request start: request_id=%s method=%s path=%s client_ip=%s",
        request_id,
        method,
        path,
        client_ip,
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "Request crash: request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            method,
            path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id

    level = "warning" if response.status_code >= 400 else "info"
    getattr(logger, level)(
        "Request complete: request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        method,
        path,
        response.status_code,
        duration_ms,
    )

    return response


@app.exception_handler(HTTPException)
async def http_exception_logger(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        "HTTP exception: request_id=%s method=%s path=%s status=%s detail=%s",
        request_id,
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def unhandled_exception_logger(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(
        "Unhandled exception: request_id=%s method=%s path=%s error=%s",
        request_id,
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ---------------------------------------------------------------------------
# Routers (ALL under /api/v1)
# ---------------------------------------------------------------------------

app.include_router(auth_router,       prefix="/api/v1")
app.include_router(users_router,      prefix="/api/v1")
app.include_router(courses_router,    prefix="/api/v1")
app.include_router(professors_router, prefix="/api/v1")
app.include_router(sections_router,   prefix="/api/v1")
app.include_router(semesters_router,  prefix="/api/v1")
app.include_router(reviews_router,    prefix="/api/v1")
app.include_router(violations_router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}