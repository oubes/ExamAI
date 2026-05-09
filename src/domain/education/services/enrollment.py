# ---- Imports ---- #
import logging
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import CursorResult
from sqlalchemy import select, delete, func, and_, exists

from src.domain.education.models.enrollment import Enrollment


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Enrollment Service ---- #
class EnrollmentService:

    # ---- Enroll User ---- #
    async def enroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_id: int,
    ) -> Enrollment:

        try:
            logger.debug(f"[EnrollmentService] enroll user={user_id} subject={subject_id}")

            stmt = select(Enrollment).where(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.subject_id == subject_id,
                )
            )

            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            record = Enrollment(
                user_id=user_id,
                subject_id=subject_id,
            )

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[EnrollmentService] enroll error: {e}", exc_info=True)
            raise


    # ---- Bulk Enroll ---- #
    async def bulk_enroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_ids: list[int],
    ) -> list[Enrollment]:

        try:
            stmt = select(Enrollment.subject_id).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)
            existing = {row[0] for row in result.all()}

            new_records = []

            for subject_id in subject_ids:
                if subject_id in existing:
                    continue

                new_records.append(
                    Enrollment(
                        user_id=user_id,
                        subject_id=subject_id,
                    )
                )

            session.add_all(new_records)
            await session.commit()

            for r in new_records:
                await session.refresh(r)

            return new_records

        except Exception as e:
            logger.error(f"[EnrollmentService] bulk_enroll error: {e}", exc_info=True)
            raise


    # ---- Unenroll User ---- #
    async def unenroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_id: int,
    ) -> bool:

        try:
            stmt = delete(Enrollment).where(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.subject_id == subject_id,
                )
            )

            result = cast(CursorResult, await session.execute(stmt))
            await session.commit()

            return result.rowcount > 0

        except Exception as e:
            logger.error(f"[EnrollmentService] unenroll error: {e}", exc_info=True)
            raise


    # ---- Bulk Unenroll ---- #
    async def bulk_unenroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_ids: list[int],
    ) -> int:

        try:
            stmt = delete(Enrollment).where(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.subject_id.in_(subject_ids),
                )
            )

            result = cast(CursorResult, await session.execute(stmt))
            await session.commit()

            return result.rowcount

        except Exception as e:
            logger.error(f"[EnrollmentService] bulk_unenroll error: {e}", exc_info=True)
            raise


    # ---- Get User Subjects ---- #
    async def get_user_subjects(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Enrollment]:

        try:
            stmt = select(Enrollment).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[EnrollmentService] get_user_subjects error: {e}", exc_info=True)
            raise


    # ---- Get Subject Users ---- #
    async def get_subject_users(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Enrollment]:

        try:
            stmt = select(Enrollment).where(
                Enrollment.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[EnrollmentService] get_subject_users error: {e}", exc_info=True)
            raise


    # ---- Check Enrollment ---- #
    async def is_enrolled(
        self,
        session: AsyncSession,
        user_id: int,
        subject_id: int,
    ) -> bool:

        try:
            stmt = select(
                exists().where(
                    and_(
                        Enrollment.user_id == user_id,
                        Enrollment.subject_id == subject_id,
                    )
                )
            )

            result = await session.execute(stmt)

            # result.scalar() may return None; ensure a bool is returned
            return bool(result.scalar())

        except Exception as e:
            logger.error(f"[EnrollmentService] is_enrolled error: {e}", exc_info=True)
            raise


    # ---- Count User Enrollments ---- #
    async def count_user_enrollments(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:

        try:
            stmt = select(func.count()).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)

            # result.scalar() may return None; ensure an int is returned
            val = result.scalar()
            return int(val or 0)

        except Exception as e:
            logger.error(f"[EnrollmentService] count_user_enrollments error: {e}", exc_info=True)
            raise


    # ---- Count Subject Enrollments ---- #
    async def count_subject_enrollments(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> int:

        try:
            stmt = select(func.count()).where(
                Enrollment.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(f"[EnrollmentService] count_subject_enrollments error: {e}", exc_info=True)
            raise


    # ---- Get User Subject IDs ---- #
    async def get_user_subject_ids(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> set[int]:

        try:
            stmt = select(Enrollment.subject_id).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)

            return {row[0] for row in result.all()}

        except Exception as e:
            logger.error(f"[EnrollmentService] get_user_subject_ids error: {e}", exc_info=True)
            raise


    # ---- Clear User Enrollments ---- #
    async def clear_user_enrollments(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:

        try:
            stmt = delete(Enrollment).where(
                Enrollment.user_id == user_id
            )

            result = await session.execute(stmt)
            await session.commit()

            return cast(CursorResult, result).rowcount

        except Exception as e:
            logger.error(f"[EnrollmentService] clear_user_enrollments error: {e}", exc_info=True)
            raise