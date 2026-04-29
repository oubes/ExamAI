# ---- Imports ---- #
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from core.config.settings import get_settings

# ---- Logging ---- #
logging = logging.getLogger(__name__)
# ---- Lifespan ---- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up")
    app.state.settings = get_settings()
    yield
    logging.info("Shutting down")