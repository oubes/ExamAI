# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.identity.models.user import User


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- User Service ---- #
class UserService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> User:

        try:
            email = payload["email"]
            user_name = payload["user_name"]

            email_stmt = select(User.id).where(User.email == email)
            username_stmt = select(User.id).where(User.user_name == user_name)

            email_result = await session.execute(email_stmt)
            username_result = await session.execute(username_stmt)

            if email_result.scalar_one_or_none():
                raise ValueError("email already exists")

            if username_result.scalar_one_or_none():
                raise ValueError("username already exists")

            record = User(
                full_name=str(payload["full_name"]),
                user_name=user_name,
                email=email,
                role=str(payload.get("role", "user")),
                password_hash=payload.get("password_hash"),
                is_active=bool(payload.get("is_active", True)),
                is_verified=bool(payload.get("is_verified", False)),
                global_learning_velocity=float(
                    payload.get("global_learning_velocity", 0.0)
                ),
                preferred_difficulty_band=float(
                    payload.get("preferred_difficulty_band", 1.0)
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[UserService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[UserService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> User | None:

        try:
            stmt = select(User).where(User.id == record_id)

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[UserService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Email ---- #
    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:

        try:
            stmt = select(User).where(User.email == email)

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[UserService] get_by_email error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Username ---- #
    async def get_by_username(
        self,
        session: AsyncSession,
        user_name: str,
    ) -> User | None:

        try:
            stmt = select(User).where(User.user_name == user_name)

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[UserService] get_by_username error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        updates: dict,
    ) -> User:
        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("user not found")

            if "email" in updates:
                email_stmt = select(User.id).where(
                    User.email == updates["email"]
                )

                email_result = await session.execute(email_stmt)

                existing = email_result.scalar_one_or_none()

                if existing and existing != record_id:
                    raise ValueError("email already exists")

                record.email = updates["email"]

            if "user_name" in updates:
                username_stmt = select(User.id).where(
                    User.user_name == updates["user_name"]
                )

                username_result = await session.execute(username_stmt)

                existing = username_result.scalar_one_or_none()

                if existing and existing != record_id:
                    raise ValueError("username already exists")

                record.user_name = updates["user_name"]

            if "full_name" in updates:
                record.full_name = str(updates["full_name"])

            if "role" in updates:
                record.role = str(updates["role"])

            if "is_active" in updates:
                record.is_active = bool(updates["is_active"])

            if "is_verified" in updates:
                record.is_verified = bool(updates["is_verified"])
                
            if "password_hash" in updates:
                record.password_hash = str(updates["password_hash"])

            if "global_learning_velocity" in updates:
                record.global_learning_velocity = float(
                    updates["global_learning_velocity"]
                )

            if "preferred_difficulty_band" in updates:
                record.preferred_difficulty_band = float(
                    updates["preferred_difficulty_band"]
                )

            await session.commit()
            await session.refresh(record)
            print(record)
            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[UserService] update error: {e}",
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
                session=session,
                record_id=record_id,
            )

            if not record:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[UserService] delete error: {e}",
                exc_info=True,
            )
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> dict:

        try:
            attempts_stmt = select(func.count()).select_from(
                User.attempts.property.mapper.class_
            ).where(
                User.attempts.property.mapper.class_.user_id == user_id
            )

            enrollments_stmt = select(func.count()).select_from(
                User.enrollments.property.mapper.class_
            ).where(
                User.enrollments.property.mapper.class_.user_id == user_id
            )

            attempts_result = await session.execute(attempts_stmt)
            enrollments_result = await session.execute(enrollments_stmt)

            return {
                "attempts": attempts_result.scalar(),
                "enrollments": enrollments_result.scalar(),
            }

        except Exception as e:
            logger.error(
                f"[UserService] stats error: {e}",
                exc_info=True,
            )
            raise