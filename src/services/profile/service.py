# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.models.user import User
from src.domain.identity.services.user import UserService


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Profile Service ---- #
class ProfileService:

    # ---- Init ---- #
    def __init__(self):

        self.user_service = UserService()


    # ---- Get Profile ---- #
    async def get_profile(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:

        try:
            return await self.user_service.get_by_id(
                session=session,
                record_id=user_id,
            )

        except Exception as e:
            logger.error(
                f"[ProfileService] get_profile error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Profile ---- #
    async def update_profile(
        self,
        session: AsyncSession,
        user_id: UUID,
        updates: dict,
    ) -> User:

        try:

            allowed_updates = {}

            # ---- Editable Fields Only ---- #
            editable_fields = {
                "full_name",
                "user_name",
                "email",
                "password_hash",
                "preferred_difficulty_band",
            }

            for key, value in updates.items():

                if key in editable_fields:
                    allowed_updates[key] = value

            return await self.user_service.update(
                session=session,
                record_id=user_id,
                updates=allowed_updates,
            )

        except Exception as e:
            logger.error(
                f"[ProfileService] update_profile error: {e}",
                exc_info=True,
            )
            raise


    # ---- Public Profile ---- #
    async def get_public_profile(
        self,
        session: AsyncSession,
        user_name: str,
    ) -> dict | None:

        try:

            record = await self.user_service.get_by_username(
                session=session,
                user_name=user_name,
            )

            if not record:
                return None

            return {
                "id": record.id,
                "full_name": record.full_name,
                "user_name": record.user_name,
                "global_learning_velocity": (
                    record.global_learning_velocity
                ),
                "preferred_difficulty_band": (
                    record.preferred_difficulty_band
                ),
                "is_verified": record.is_verified,
            }

        except Exception as e:
            logger.error(
                f"[ProfileService] get_public_profile error: {e}",
                exc_info=True,
            )
            raise


    # ---- Profile Stats ---- #
    async def get_profile_stats(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> dict:

        try:

            return await self.user_service.stats(
                session=session,
                user_id=user_id,
            )

        except Exception as e:
            logger.error(
                f"[ProfileService] get_profile_stats error: {e}",
                exc_info=True,
            )
            raise