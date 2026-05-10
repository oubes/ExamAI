# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.attempts.models.answer import Answer
from src.domain.attempts.models.attempt import ExamAttempt
from src.domain.questions.models.question import Question
from src.domain.questions.models.option import QuestionOption


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Answer Service ---- #
class AnswerService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> Answer:

        try:
            attempt_id = payload["attempt_id"]
            question_id = payload["question_id"]
            option_id = payload.get("option_id")

            attempt_stmt = select(ExamAttempt.id).where(
                ExamAttempt.id == attempt_id
            )

            question_stmt = select(Question.id).where(
                Question.id == question_id
            )

            attempt_result = await session.execute(attempt_stmt)
            question_result = await session.execute(question_stmt)

            if not attempt_result.scalar_one_or_none():
                raise ValueError("attempt not found")

            if not question_result.scalar_one_or_none():
                raise ValueError("question not found")

            if option_id:
                option_stmt = select(QuestionOption.id).where(
                    QuestionOption.id == option_id
                )

                option_result = await session.execute(option_stmt)

                if not option_result.scalar_one_or_none():
                    raise ValueError("option not found")

            record = Answer(
                attempt_id=attempt_id,
                question_id=question_id,
                option_id=option_id,
                student_answer=str(payload["student_answer"]),
                score=float(payload.get("score", 0.0)),
                confidence=float(payload.get("confidence", 0.0)),
                time_spent_sec=payload.get("time_spent_sec"),
                partial_credit=float(payload.get("partial_credit", 0.0)),
                is_correct=bool(payload.get("is_correct", False)),
                needs_review=bool(payload.get("needs_review", False)),
                reviewed_by_human=bool(
                    payload.get("reviewed_by_human", False)
                ),
                human_override_score=payload.get(
                    "human_override_score"
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[AnswerService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[AnswerService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Answer]:

        try:
            if not payloads:
                return []

            attempt_ids = {p["attempt_id"] for p in payloads}
            question_ids = {p["question_id"] for p in payloads}

            attempt_stmt = select(ExamAttempt.id).where(
                ExamAttempt.id.in_(attempt_ids)
            )

            question_stmt = select(Question.id).where(
                Question.id.in_(question_ids)
            )

            attempt_result = await session.execute(attempt_stmt)
            question_result = await session.execute(question_stmt)

            existing_attempts = set(
                attempt_result.scalars().all()
            )

            existing_questions = set(
                question_result.scalars().all()
            )

            if attempt_ids - existing_attempts:
                raise ValueError("invalid attempt_ids")

            if question_ids - existing_questions:
                raise ValueError("invalid question_ids")

            records: list[Answer] = [
                Answer(
                    attempt_id=p["attempt_id"],
                    question_id=p["question_id"],
                    option_id=p.get("option_id"),
                    student_answer=str(p["student_answer"]),
                    score=float(p.get("score", 0.0)),
                    confidence=float(p.get("confidence", 0.0)),
                    time_spent_sec=p.get("time_spent_sec"),
                    partial_credit=float(p.get("partial_credit", 0.0)),
                    is_correct=bool(p.get("is_correct", False)),
                    needs_review=bool(p.get("needs_review", False)),
                    reviewed_by_human=bool(
                        p.get("reviewed_by_human", False)
                    ),
                    human_override_score=p.get(
                        "human_override_score"
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
                f"[AnswerService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        answer_id: UUID,
    ) -> bool:

        try:
            stmt = select(Answer.id).where(
                Answer.id == answer_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[AnswerService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        answer_id: UUID,
    ) -> Answer | None:

        try:
            stmt = select(Answer).where(Answer.id == answer_id)

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[AnswerService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        answer_id: UUID,
    ) -> Answer | None:

        try:
            stmt = (
                select(Answer)
                .options(
                    selectinload(Answer.attempt),
                    selectinload(Answer.question),
                    selectinload(Answer.option),
                    selectinload(Answer.feedback),
                )
                .where(Answer.id == answer_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[AnswerService] get_full error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Attempt ---- #
    async def list_by_attempt(
        self,
        session: AsyncSession,
        attempt_id: UUID,
    ) -> list[Answer]:

        try:
            stmt = (
                select(Answer)
                .where(Answer.attempt_id == attempt_id)
                .order_by(Answer.question_id.asc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[AnswerService] list_by_attempt error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Score ---- #
    async def update_score(
        self,
        session: AsyncSession,
        answer_id: UUID,
        score: float,
        is_correct: bool,
    ) -> Answer:

        try:
            record = await self.get_by_id(
                session=session,
                answer_id=answer_id,
            )

            if not record:
                raise ValueError("answer not found")

            record.score = score
            record.is_correct = is_correct

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[AnswerService] update_score error: {e}",
                exc_info=True,
            )
            raise


    # ---- Mark Review ---- #
    async def mark_review(
        self,
        session: AsyncSession,
        answer_id: UUID,
        needs_review: bool,
    ) -> Answer:

        try:
            record = await self.get_by_id(
                session=session,
                answer_id=answer_id,
            )

            if not record:
                raise ValueError("answer not found")

            record.needs_review = needs_review

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[AnswerService] mark_review error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        answer_id: UUID,
    ) -> bool:

        try:
            record = await self.get_by_id(
                session=session,
                answer_id=answer_id,
            )

            if not record:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[AnswerService] delete error: {e}",
                exc_info=True,
            )
            raise