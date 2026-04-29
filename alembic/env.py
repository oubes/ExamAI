# ----- Imports ----- #
from logging.config import fileConfig
import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.db.base import Base
from src.core.di.settings import get_settings

# ---- Config ---- #
config = context.config

# ---- Logging ---- #
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- Metadata ---- #
target_metadata = Base.metadata

# ---- Settings ---- #
settings = get_settings()


# ---------- Offline Migrations ---------- #
def run_migrations_offline() -> None:
    context.configure(
        url=settings.postgres_full_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------- Migration Logic ---------- #
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # مهم لـ vector + تغييرات types
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------- Online Migrations ---------- #
def run_migrations_online() -> None:

    connectable = async_engine_from_config(
        {
            "sqlalchemy.url": settings.postgres_full_url
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio.run(run())


# ---------- Entry Point ---------- #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()