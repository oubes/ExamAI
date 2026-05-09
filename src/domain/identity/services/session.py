# ---- imports ---- #
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.domain.identity.models.session import UserSession


# ---- Session Service ---- #
class SessionService:

    def __init__(self):
        self.model = UserSession

    # ---------- get by id ---------- #
    async def get_by_id(self, session: AsyncSession, session_id: UUID) -> UserSession | None:
        return await session.get(self.model, session_id)

    # ---------- list all ---------- #
    async def list_all(self, session: AsyncSession) -> list[UserSession]:

        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    # ---------- get by filters ---------- #
    async def get_by_filters(self, session: AsyncSession, **filters) -> UserSession | None:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return result.scalar_one_or_none()

    # ---------- list by filters ---------- #
    async def list_by_filters(self, session: AsyncSession, **filters) -> list[UserSession]:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return list(result.scalars().all())

    # ---------- create ---------- #
    async def create(self, session: AsyncSession, entity: UserSession) -> UserSession:

        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    # ---------- update by id ---------- #
    async def update_by_id(
        self,
        session: AsyncSession,
        session_id: UUID,
        updates: dict,
    ) -> UserSession | None:

        entity = await session.get(self.model, session_id)

        if not entity:
            return None

        for k, v in updates.items():
            setattr(entity, k, v)

        await session.commit()
        await session.refresh(entity)
        return entity

    # ---------- delete by id ---------- #
    async def delete_by_id(self, session: AsyncSession, session_id: UUID) -> bool:

        entity = await session.get(self.model, session_id)

        if not entity:
            return False

        await session.delete(entity)
        await session.commit()
        return True

    # ---------- exists ---------- #
    async def exists(self, session: AsyncSession, **filters) -> bool:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return result.scalar_one_or_none() is not None