# ---- Imports ---- #
from contextlib import asynccontextmanager

# ---- Lifespan ---- #
@asynccontextmanager
async def lifespan(app):
    print("Starting up")
    yield
    print("Shutting down")