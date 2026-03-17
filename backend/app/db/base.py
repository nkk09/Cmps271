"""
Async database engine, session factory, and Base.
This is the single source of truth for DB setup — core/database.py is not used.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _normalize_asyncpg_url(database_url: str) -> tuple[str, dict]:
    """Make asyncpg-compatible URL/connect args from env DATABASE_URL."""
    url = make_url(database_url)
    connect_args: dict = {}

    # asyncpg does not accept "sslmode" in connect kwargs.
    # Keep compatibility with common Postgres DSNs like ?sslmode=require.
    if url.drivername == "postgresql+asyncpg" and "sslmode" in url.query:
        sslmode = (url.query.get("sslmode") or "").lower()
        url = url.difference_update_query(["sslmode"])

        if sslmode in {"require", "verify-ca", "verify-full"}:
            connect_args["ssl"] = True
        elif sslmode == "disable":
            connect_args["ssl"] = False

    return url.render_as_string(hide_password=False), connect_args


normalized_database_url, normalized_connect_args = _normalize_asyncpg_url(settings.DATABASE_URL)


engine = create_async_engine(
    normalized_database_url,
    echo=settings.ENV == "dev",
    pool_pre_ping=True,
    pool_recycle=280,  # recycle before Neon's ~5-minute idle timeout
    connect_args=normalized_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async session, commits on success, rolls back on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise