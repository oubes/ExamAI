# ---- Imports ---- #
import logging
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.models.session import UserSession
from src.domain.identity.models.user import User


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- User Session Service ---- #
class SessionService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict | UserSession,
    ) -> UserSession:

        try:
            if isinstance(payload, UserSession):
                record = payload
            else:
                user_id = payload["user_id"]

                user_stmt = select(User.id).where(User.id == user_id)
                user_result = await session.execute(user_stmt)

                if not user_result.scalar_one_or_none():
                    raise ValueError("user not found")

                record = UserSession(
                    user_id=user_id,
                    is_active=bool(payload.get("is_active", True)),
                    ip_address=payload.get("ip_address"),
                    user_agent=payload.get("user_agent"),
                    expires_at=payload["expires_at"],
                    last_seen_at=payload.get("last_seen_at"),
                )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SessionService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> UserSession | None:

        try:
            stmt = select(UserSession).where(
                UserSession.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[SessionService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Filters ---- #
    async def list_by_filters(
        self,
        session: AsyncSession,
        user_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[UserSession]:

        try:
            stmt = select(UserSession)

            if user_id:
                stmt = stmt.where(UserSession.user_id == user_id)

            if is_active is not None:
                stmt = stmt.where(UserSession.is_active == is_active)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[SessionService] list_by_filters error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        updates: dict,
    ) -> UserSession:

        try:
            record = await self.get_by_id(
                session,
                record_id,
            )

            if not record:
                raise ValueError("session not found")

            if "user_id" in updates:
                raise ValueError("user_id is immutable")

            if "is_active" in updates:
                record.is_active = bool(updates["is_active"])

            if "ip_address" in updates:
                record.ip_address = updates["ip_address"]

            if "user_agent" in updates:
                record.user_agent = updates["user_agent"]

            if "expires_at" in updates:
                record.expires_at = updates["expires_at"]

            if "last_seen_at" in updates:
                record.last_seen_at = updates["last_seen_at"]

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SessionService] update error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        try:
            record = await self.get_by_id(
                session,
                record_id,
            )

            if not record:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SessionService] delete error: {e}",
                exc_info=True,
            )
            raise


    # ---- Deactivate ---- #
    async def deactivate(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> None:

        try:
            record = await self.get_by_id(
                session,
                record_id,
            )

            if not record:
                raise ValueError("session not found")

            record.is_active = False
            record.last_seen_at = datetime.now(timezone.utc) # type: ignore

            await session.commit()

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SessionService] deactivate error: {e}",
                exc_info=True,
            )
            raise