# ---- Imports ---- #
from contextlib import asynccontextmanager
from fastapi import FastAPI

# ---- Lifespan ---- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    yield
    print("Shutting down")