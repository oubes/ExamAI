# ----- Imports ---- #
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.di.settings import get_settings
import logging

# ---- logging ---- #
logger = logging.getLogger(__name__)

# ---- Settings ---- #
settings = get_settings()

# ------------ Database ------------ #
# ---- Create Engine ---- #
engine = create_async_engine(
    url=settings.postgres_full_url,
    echo=settings.postgres_orm_echo,
    pool_pre_ping=settings.postgres_pool_pre_ping,
    pool_size=settings.postgres_pool_size,
    max_overflow=settings.postgres_max_overflow,
    pool_recycle=settings.postgres_pool_recycle,
    pool_timeout=settings.postgres_pool_timeout,
)

# ---- Create Session Local ---- #
session_local = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=settings.postgres_auto_commit,
    autoflush=settings.postgres_auto_flush,
    expire_on_commit=settings.postgres_expire_on_commit,
)