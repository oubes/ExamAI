# ---- imports ---- #
from typing import TypeVar, Generic, Type, Optional, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


# ---- Identity Service ---- #
class IdentityService(Generic[T]):

    def __init__(self, model: Type[T]):
        self.model = model

    # ---------- get by id ---------- #
    async def get_by_id(
        self,
        session: AsyncSession,
        entity_id: Any,
    ) -> Optional[T]:

        return await session.get(self.model, entity_id)

    # ---------- list all ---------- #
    async def list_all(
        self,
        session: AsyncSession,
    ) -> list[T]:

        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    # ---------- get by filters ---------- #
    async def get_by_filters(
        self,
        session: AsyncSession,
        **filters,
    ) -> Optional[T]:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return result.scalar_one_or_none()

    # ---------- list by filters ---------- #
    async def list_by_filters(
        self,
        session: AsyncSession,
        **filters,
    ) -> list[T]:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return list(result.scalars().all())

    # ---------- create ---------- #
    async def create(
        self,
        session: AsyncSession,
        entity: T,
    ) -> T:

        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    # ---------- update by id ---------- #
    async def update_by_id(
        self,
        session: AsyncSession,
        entity_id: Any,
        updates: dict,
    ) -> Optional[T]:

        entity = await session.get(self.model, entity_id)

        if not entity:
            return None

        for k, v in updates.items():
            setattr(entity, k, v)

        await session.commit()
        await session.refresh(entity)
        return entity

    # ---------- delete by id ---------- #
    async def delete_by_id(
        self,
        session: AsyncSession,
        entity_id: Any,
    ) -> bool:

        entity = await session.get(self.model, entity_id)

        if not entity:
            return False

        await session.delete(entity)
        await session.commit()

        return True

    # ---------- exists ---------- #
    async def exists(
        self,
        session: AsyncSession,
        **filters,
    ) -> bool:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return result.scalar_one_or_none() is not None