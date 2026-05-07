# ---- imports ---- #
import logging
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.academic.models.exam import Exam


# ---- logging ---- #
logger = logging.getLogger(__name__)


# -------------------- exam service -------------------- #
class ExamService:

    # ---- create exam ---- #
    async def create(
        self,
        session: AsyncSession,
        subject_id: int,
        title: str,
        time_limit: int,
    ) -> Exam:

        try:
            logger.debug(f"[ExamService] create subject_id={subject_id}")

            exam = Exam(
                subject_id=subject_id,
                title=title,
                time_limit=time_limit,
            )

            session.add(exam)

            await session.commit()
            await session.refresh(exam)

            return exam

        except Exception as e:
            logger.error(f"[ExamService] create failed: {str(e)}", exc_info=True)
            raise


    # ---- get by id ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        exam_id: int,
    ) -> Exam | None:

        try:
            result = await session.execute(
                select(Exam).where(Exam.id == exam_id)
            )

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[ExamService] get_by_id failed: {str(e)}", exc_info=True)
            raise


    # ---- list by subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Exam]:

        try:
            result = await session.execute(
                select(Exam).where(Exam.subject_id == subject_id)
            )

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[ExamService] list_by_subject failed: {str(e)}", exc_info=True)
            raise


    # ---- update exam ---- #
    async def update(
        self,
        session: AsyncSession,
        exam_id: int,
        updates: dict,
    ) -> Exam:

        try:
            exam = await session.get(Exam, exam_id)

            if not exam:
                raise ValueError("Exam not found")

            for k, v in updates.items():
                setattr(exam, k, v)

            await session.commit()
            await session.refresh(exam)

            return exam

        except Exception as e:
            logger.error(f"[ExamService] update failed: {str(e)}", exc_info=True)
            raise


    # ---- delete exam ---- #
    async def delete(
        self,
        session: AsyncSession,
        exam_id: int,
    ) -> bool:

        try:
            result = await session.execute(
                delete(Exam).where(Exam.id == exam_id)
            )

            await session.commit()

            affected = getattr(result, "rowcount", 0)

            return bool(affected and affected > 0)

        except Exception as e:
            logger.error(f"[ExamService] delete failed: {str(e)}", exc_info=True)
            raise


    # ---- bulk create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        exams: list[dict],
    ) -> list[Exam]:

        try:
            objects = [
                Exam(
                    subject_id=e["subject_id"],
                    title=e["title"],
                    time_limit=e["time_limit"],
                )
                for e in exams
            ]

            session.add_all(objects)

            await session.commit()

            for obj in objects:
                await session.refresh(obj)

            return objects

        except Exception as e:
            logger.error(f"[ExamService] bulk_create failed: {str(e)}", exc_info=True)
            raise


    # ---- exists check ---- #
    async def exists(
        self,
        session: AsyncSession,
        exam_id: int,
    ) -> bool:

        try:
            exam = await session.get(Exam, exam_id)
            return exam is not None

        except Exception as e:
            logger.error(f"[ExamService] exists failed: {str(e)}", exc_info=True)
            raise


    # ---- delete by subject ---- #
    async def delete_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> int:

        try:
            result = await session.execute(
                delete(Exam).where(Exam.subject_id == subject_id)
            )

            await session.commit()

            affected = getattr(result, "rowcount", 0)

            return int(affected or 0)

        except Exception as e:
            logger.error(f"[ExamService] delete_by_subject failed: {str(e)}", exc_info=True)
            raise