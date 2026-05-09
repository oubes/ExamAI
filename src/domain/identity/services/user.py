# ---- imports ---- #
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.models.user import User


# ---- User Service ---- #
class UserService:

    def __init__(self):
        self.model = User

    # ---------- get by id ---------- #
    async def get_by_id(self, session: AsyncSession, user_id: str) -> User | None:
        return await session.get(self.model, user_id)

    # ---------- list all ---------- #
    async def list_all(self, session: AsyncSession) -> list[User]:

        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    # ---------- get by filters ---------- #
    async def get_by_filters(self, session: AsyncSession, **filters) -> User | None:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return result.scalar_one_or_none()

    # ---------- list by filters ---------- #
    async def list_by_filters(self, session: AsyncSession, **filters) -> list[User]:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return list(result.scalars().all())

    # ---------- create ---------- #
    async def create(self, session: AsyncSession, user: User) -> User:

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    # ---------- update by id ---------- #
    async def update_by_id(
        self,
        session: AsyncSession,
        user_id: str,
        updates: dict,
    ) -> User | None:

        user = await session.get(self.model, user_id)

        if not user:
            return None

        for k, v in updates.items():
            setattr(user, k, v)

        await session.commit()
        await session.refresh(user)
        return user

    # ---------- delete by id ---------- #
    async def delete_by_id(self, session: AsyncSession, user_id: str) -> bool:

        user = await session.get(self.model, user_id)

        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    # ---------- exists ---------- #
    async def exists(self, session: AsyncSession, **filters) -> bool:

        result = await session.execute(
            select(self.model).filter_by(**filters)
        )

        return result.scalar_one_or_none() is not None