# ---- Imports ---- #
from sqlalchemy import text
from src.infra.db.base import Base
from src.infra.db.session import engine
# ---------- Init DB ---------- #
async def init_db():

    # ---- Begin Transaction ---- #
    async with engine.begin() as conn:

        # ---- Create Tables ---- #
        await conn.run_sync(Base.metadata.create_all)