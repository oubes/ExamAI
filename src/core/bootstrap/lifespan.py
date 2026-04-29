# ---- Imports ---- #
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from src.db.init_db import init_db
from src.core.di.settings import get_settings

# ---- Logging ---- #
logging = logging.getLogger(__name__)
# ---- Lifespan ---- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ---- #
    logging.info("Starting up")
    print(get_settings().postgres_full_url)
    await init_db()
    
    yield
    
    # ---- Shutdown ---- #
    logging.info("Shutting down")