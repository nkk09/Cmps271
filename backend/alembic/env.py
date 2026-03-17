import asyncio
import os
from logging.config import fileConfig
from dotenv import load_dotenv

# Load .env before importing anything from app — order matters
load_dotenv()  # looks for .env in cwd; use load_dotenv("path/to/.env") if needed

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.db.base import Base, _normalize_asyncpg_url
import app.models 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the URL from environment so secrets never live in alembic.ini
normalized_url, _ = _normalize_asyncpg_url(os.environ["DATABASE_URL"])
config.set_main_option("sqlalchemy.url", normalized_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (outputs SQL to stdout)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations with a live async DB connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # NullPool is important for migrations
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())