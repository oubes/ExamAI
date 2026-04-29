# ---- Imports ---- #
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config.settings import get_settings

# ---- Lifespan ---- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    app.state.settings = get_settings()
    yield
    print("Shutting down")