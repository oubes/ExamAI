# ---- Imports ---- #
from src.infra.db.session import session_local
from functools import lru_cache

# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session