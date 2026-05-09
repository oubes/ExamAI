# ---- Imports ---- #
from src.infra.db.session import session_local

# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session