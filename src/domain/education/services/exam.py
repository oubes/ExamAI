# ---- Imports ---- #
import logging
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domain.education.models.exam import Exam


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Exam Service ---- #
class ExamService:

    # ---- Create Exam ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Exam:

        try:
            logger.debug(f"[ExamService] create: {data}")

            record = Exam(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[ExamService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        exam_id: int,
    ) -> Exam | None:

        try:
            return await session.get(Exam, exam_id)

        except Exception as e:
            logger.error(f"[ExamService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By Subject ---- #
    async def get_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Exam]:

        try:
            stmt = select(Exam).where(
                Exam.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[ExamService] get_by_subject error: {e}", exc_info=True)
            raise


    # ---- Update Exam ---- #
    async def update(
        self,
        session: AsyncSession,
        exam_id: int,
        updates: dict,
    ) -> Exam:

        try:
            record = await session.get(Exam, exam_id)

            if not record:
                raise ValueError("exam not found")

            # ---- protected fields ---- #
            protected = {"id", "subject_id"}

            for key, value in updates.items():
                if key in protected:
                    continue
                setattr(record, key, value)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[ExamService] update error: {e}", exc_info=True)
            raise


    # ---- Delete Exam ---- #
    async def delete(
        self,
        session: AsyncSession,
        exam_id: int,
    ) -> bool:

        try:
            record = await session.get(Exam, exam_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[ExamService] delete error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        subject_id: int | None = None,
    ) -> list[Exam]:

        try:
            query = query.strip()

            if not query:
                return []

            stmt = select(Exam).where(
                Exam.title.ilike(f"%{query}%")
            )

            if subject_id:
                stmt = stmt.where(Exam.subject_id == subject_id)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[ExamService] search error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> dict:

        try:
            stmt = select(func.count()).where(
                Exam.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return {
                "total": result.scalar()
            }

        except Exception as e:
            logger.error(f"[ExamService] stats error: {e}", exc_info=True)
            raise


    # ---- Parse Scope Config ---- #
    async def parse_scope(
        self,
        session: AsyncSession,
        exam_id: int,
    ) -> dict:

        try:
            exam = await session.get(Exam, exam_id)

            if not exam:
                raise ValueError("exam not found")

            if not exam.scope_config:
                return {}

            try:
                return json.loads(exam.scope_config)
            except Exception:
                raise ValueError("invalid scope_config format")

        except Exception as e:
            logger.error(f"[ExamService] parse_scope error: {e}", exc_info=True)
            raise