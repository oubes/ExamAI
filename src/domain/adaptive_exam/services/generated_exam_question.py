# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.adaptive_exam.models.generated_exam_question import GeneratedExamQuestion
from src.domain.adaptive_exam.models.generated_exam_session import GeneratedExamSession
from src.domain.questions.models.question import Question


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Generated Exam Question Service ---- #
class GeneratedExamQuestionService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> GeneratedExamQuestion:

        try:
            session_id = payload["session_id"]
            question_id = payload["question_id"]

            session_stmt = select(GeneratedExamSession.id).where(
                GeneratedExamSession.id == session_id
            )

            question_stmt = select(Question.id).where(
                Question.id == question_id
            )

            session_result = await session.execute(session_stmt)
            question_result = await session.execute(question_stmt)

            if not session_result.scalar_one_or_none():
                raise ValueError("session not found")

            if not question_result.scalar_one_or_none():
                raise ValueError("question not found")

            record = GeneratedExamQuestion(
                session_id=session_id,
                question_id=question_id,
                question_order=int(payload.get("question_order", 0)),
                selection_reason=payload.get("selection_reason"),
                predicted_difficulty_fit=float(
                    payload.get("predicted_difficulty_fit", 0.0)
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamQuestionService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamQuestionService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[GeneratedExamQuestion]:

        try:
            if not payloads:
                return []

            session_ids = {p["session_id"] for p in payloads}
            question_ids = {p["question_id"] for p in payloads}

            session_stmt = select(GeneratedExamSession.id).where(
                GeneratedExamSession.id.in_(session_ids)
            )

            question_stmt = select(Question.id).where(
                Question.id.in_(question_ids)
            )

            session_result = await session.execute(session_stmt)
            question_result = await session.execute(question_stmt)

            existing_sessions = set(session_result.scalars().all())
            existing_questions = set(question_result.scalars().all())

            if session_ids - existing_sessions:
                raise ValueError("invalid session_ids")

            if question_ids - existing_questions:
                raise ValueError("invalid question_ids")

            records: list[GeneratedExamQuestion] = [
                GeneratedExamQuestion(
                    session_id=p["session_id"],
                    question_id=p["question_id"],
                    question_order=int(p.get("question_order", 0)),
                    selection_reason=p.get("selection_reason"),
                    predicted_difficulty_fit=float(
                        p.get("predicted_difficulty_fit", 0.0)
                    ),
                )
                for p in payloads
            ]

            session.add_all(records)

            await session.commit()

            for r in records:
                await session.refresh(r)

            return records

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamQuestionService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        try:
            stmt = select(GeneratedExamQuestion.id).where(
                GeneratedExamQuestion.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[GeneratedExamQuestionService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> GeneratedExamQuestion | None:

        try:
            stmt = select(GeneratedExamQuestion).where(
                GeneratedExamQuestion.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[GeneratedExamQuestionService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> GeneratedExamQuestion | None:

        try:
            stmt = (
                select(GeneratedExamQuestion)
                .options(
                    selectinload(GeneratedExamQuestion.session),
                    selectinload(GeneratedExamQuestion.question),
                )
                .where(GeneratedExamQuestion.id == record_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[GeneratedExamQuestionService] get_full error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Session ---- #
    async def list_by_session(
        self,
        session: AsyncSession,
        session_id: UUID,
    ) -> list[GeneratedExamQuestion]:

        try:
            stmt = (
                select(GeneratedExamQuestion)
                .where(GeneratedExamQuestion.session_id == session_id)
                .order_by(GeneratedExamQuestion.question_order.asc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[GeneratedExamQuestionService] list_by_session error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Order ---- #
    async def update_order(
        self,
        session: AsyncSession,
        record_id: UUID,
        question_order: int,
    ) -> GeneratedExamQuestion:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("record not found")

            record.question_order = question_order

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamQuestionService] update_order error: {e}",
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
                f"[GeneratedExamQuestionService] delete error: {e}",
                exc_info=True,
            )
            raise