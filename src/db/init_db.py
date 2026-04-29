from db.base import Base
from db.session import engine

from db.models import identity

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)