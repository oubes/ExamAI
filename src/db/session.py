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
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_timeout=30,
)

# ---- Create Session Local ---- #
session_local = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)