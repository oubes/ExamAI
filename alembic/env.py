# ----- Imports ---- #
from logging.config import fileConfig
from alembic import context
from src.db.base import Base
from src.db.session import engine

# ---- Config ---- #
config = context.config

# ---- Logging ---- #
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- Metadata ---- #
target_metadata = Base.metadata


# ---------- Offline Migrations ---------- #
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------- Online Migrations ---------- #
def run_migrations_online() -> None:
    connectable = engine.sync_engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------- Run Mode ---------- #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()