# ---- imports ---- #
import logging
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.academic.models.enrollment import Enrollment


# ---- logging ---- #
logger = logging.getLogger(__name__)


# -------------------- enrollment service -------------------- #
class EnrollmentService:

    async def enroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_id: int,
    ) -> Enrollment:

        try:
            logger.debug(f"[EnrollmentService] enroll user_id={user_id} subject_id={subject_id}")

            result = await session.execute(
                select(Enrollment).where(
                    and_(
                        Enrollment.user_id == user_id,
                        Enrollment.subject_id == subject_id,
                    )
                )
            )

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
            logger.error(f"[EnrollmentService] enroll failed: {str(e)}", exc_info=True)
            raise


    async def bulk_enroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_ids: list[int],
        skip_existing: bool = True,
    ) -> list[Enrollment]:

        try:
            logger.debug(f"[EnrollmentService] bulk_enroll user_id={user_id}")

            result = await session.execute(
                select(Enrollment.subject_id).where(
                    Enrollment.user_id == user_id
                )
            )

            existing = set(result.scalars().all())

            new_records: list[Enrollment] = []

            for subject_id in subject_ids:
                if skip_existing and subject_id in existing:
                    continue

                new_records.append(
                    Enrollment(
                        user_id=user_id,
                        subject_id=subject_id,
                    )
                )

            if not new_records:
                return []

            session.add_all(new_records)

            await session.commit()

            for r in new_records:
                await session.refresh(r)

            return new_records

        except Exception as e:
            logger.error(f"[EnrollmentService] bulk_enroll failed: {str(e)}", exc_info=True)
            raise


    async def unenroll(
        self,
        session: AsyncSession,
        user_id: int,
        subject_id: int,
    ) -> bool:

        try:
            logger.debug(f"[EnrollmentService] unenroll user_id={user_id} subject_id={subject_id}")

            result = await session.execute(
                delete(Enrollment).where(
                    and_(
                        Enrollment.user_id == user_id,
                        Enrollment.subject_id == subject_id,
                    )
                )
            )

            await session.commit()

            # FIX: rowcount typing issue safe handling
            affected = getattr(result, "rowcount", None)

            return bool(affected and affected > 0)

        except Exception as e:
            logger.error(f"[EnrollmentService] unenroll failed: {str(e)}", exc_info=True)
            raise


    async def get_user_enrollments(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Enrollment]:

        try:
            result = await session.execute(
                select(Enrollment).where(
                    Enrollment.user_id == user_id
                )
            )

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[EnrollmentService] get_user_enrollments failed: {str(e)}", exc_info=True)
            raise


    async def get_subject_enrollments(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Enrollment]:

        try:
            result = await session.execute(
                select(Enrollment).where(
                    Enrollment.subject_id == subject_id
                )
            )

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[EnrollmentService] get_subject_enrollments failed: {str(e)}", exc_info=True)
            raise


    async def is_enrolled(
        self,
        session: AsyncSession,
        user_id: int,
        subject_id: int,
    ) -> bool:

        try:
            result = await session.execute(
                select(Enrollment).where(
                    and_(
                        Enrollment.user_id == user_id,
                        Enrollment.subject_id == subject_id,
                    )
                )
            )

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(f"[EnrollmentService] is_enrolled failed: {str(e)}", exc_info=True)
            raise


    async def delete_user_enrollments(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:

        try:
            result = await session.execute(
                delete(Enrollment).where(
                    Enrollment.user_id == user_id
                )
            )

            await session.commit()

            affected = getattr(result, "rowcount", 0)
            return int(affected or 0)

        except Exception as e:
            logger.error(f"[EnrollmentService] delete_user_enrollments failed: {str(e)}", exc_info=True)
            raise


    async def delete_subject_enrollments(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> int:

        try:
            result = await session.execute(
                delete(Enrollment).where(
                    Enrollment.subject_id == subject_id
                )
            )

            await session.commit()

            affected = getattr(result, "rowcount", 0)
            return int(affected or 0)

        except Exception as e:
            logger.error(f"[EnrollmentService] delete_subject_enrollments failed: {str(e)}", exc_info=True)
            raise