"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.courses import (
    courses_router,
    professors_router,
    sections_router,
    semesters_router,
)
from app.api.reviews import router as reviews_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "dev" else [],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router,       prefix="/api/v1")
app.include_router(users_router,      prefix="/api/v1")
app.include_router(courses_router,    prefix="/api/v1")
app.include_router(professors_router, prefix="/api/v1")
app.include_router(sections_router,   prefix="/api/v1")
app.include_router(semesters_router,  prefix="/api/v1")
app.include_router(reviews_router,    prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}
