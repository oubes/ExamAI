# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.education.models.enrollment import Enrollment
from src.domain.education.models.subject import Subject
from src.domain.identity.models.user import User


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Enrollment Service ---- #
class EnrollmentService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        user_id: UUID,
        subject_id: UUID,
    ) -> Enrollment:

        try:
            user_stmt = select(User.id).where(User.id == user_id)
            subject_stmt = select(Subject.id).where(
                Subject.id == subject_id
            )

            user_result = await session.execute(user_stmt)
            subject_result = await session.execute(subject_stmt)

            if not user_result.scalar_one_or_none():
                raise ValueError("user not found")

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            exists_stmt = select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.subject_id == subject_id,
            )

            exists_result = await session.execute(exists_stmt)

            if exists_result.scalar_one_or_none():
                raise ValueError("already enrolled")

            record = Enrollment(
                user_id=user_id,
                subject_id=subject_id,
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[EnrollmentService] create integrity error: {e}",
                exc_info=True,
            )

            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[EnrollmentService] create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        user_id: UUID,
        subject_ids: list[UUID],
    ) -> list[Enrollment]:

        try:
            if not subject_ids:
                return []

            user_stmt = select(User.id).where(User.id == user_id)
            user_result = await session.execute(user_stmt)

            if not user_result.scalar_one_or_none():
                raise ValueError("user not found")

            existing_stmt = select(Enrollment.subject_id).where(
                Enrollment.user_id == user_id,
                Enrollment.subject_id.in_(subject_ids),
            )

            existing_result = await session.execute(existing_stmt)

            existing_subjects = set(existing_result.scalars().all())

            to_create = [
                sid for sid in subject_ids
                if sid not in existing_subjects
            ]

            records = [
                Enrollment(user_id=user_id, subject_id=sid)
                for sid in to_create
            ]

            session.add_all(records)

            await session.commit()

            for record in records:
                await session.refresh(record)

            return records

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[EnrollmentService] bulk_create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        user_id: UUID,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = select(Enrollment.user_id).where(
                Enrollment.user_id == user_id,
                Enrollment.subject_id == subject_id,
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[EnrollmentService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By User ---- #
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Enrollment]:

        try:
            stmt = (
                select(Enrollment)
                .where(Enrollment.user_id == user_id)
                .options(selectinload(Enrollment.subject))
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[EnrollmentService] list_by_user error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Enrollment]:

        try:
            stmt = (
                select(Enrollment)
                .where(Enrollment.subject_id == subject_id)
                .options(selectinload(Enrollment.user))
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[EnrollmentService] list_by_subject error: {e}",
                exc_info=True,
            )
            raise


    # ---- Count ---- #
    async def count(
        self,
        session: AsyncSession,
    ) -> int:

        try:
            stmt = select(func.count()).select_from(Enrollment)

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[EnrollmentService] count error: {e}",
                exc_info=True,
            )
            raise


    # ---- Count By User ---- #
    async def count_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> int:

        try:
            stmt = select(func.count()).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[EnrollmentService] count_by_user error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        user_id: UUID,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.subject_id == subject_id,
            )

            result = await session.execute(stmt)

            await session.commit()

            affected_rows = result.rowcount # type: ignore

            return bool(affected_rows and affected_rows > 0)

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[EnrollmentService] delete error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete By User ---- #
    async def delete_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> int:

        try:
            stmt = delete(Enrollment).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)

            await session.commit()

            affected_rows = result.rowcount # type: ignore

            return int(affected_rows or 0)

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[EnrollmentService] delete_by_user error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete By Subject ---- #
    async def delete_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> int:

        try:
            stmt = delete(Enrollment).where(
                Enrollment.subject_id == subject_id
            )

            result = await session.execute(stmt)

            await session.commit()

            affected_rows = result.rowcount # type: ignore

            return int(affected_rows or 0)

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[EnrollmentService] delete_by_subject error: {e}",
                exc_info=True,
            )
            raise