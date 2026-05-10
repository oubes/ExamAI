# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.questions.models.model_answer import ModelAnswer
from src.domain.questions.models.question import Question


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Model Answer Service ---- #
class ModelAnswerService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> ModelAnswer:

        try:
            question_id = payload["question_id"]

            question_stmt = select(Question.id).where(
                Question.id == question_id
            )

            question_result = await session.execute(question_stmt)

            if not question_result.scalar_one_or_none():
                raise ValueError("question not found")

            existing_stmt = select(ModelAnswer.id).where(
                ModelAnswer.question_id == question_id
            )

            existing_result = await session.execute(existing_stmt)

            if existing_result.scalar_one_or_none():
                raise ValueError("model answer already exists")

            record = ModelAnswer(
                question_id=question_id,
                answer_text=str(payload["answer_text"]),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[ModelAnswerService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ModelAnswerService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> ModelAnswer | None:

        try:
            stmt = select(ModelAnswer).where(
                ModelAnswer.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ModelAnswerService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Question ---- #
    async def get_by_question(
        self,
        session: AsyncSession,
        question_id: UUID,
    ) -> ModelAnswer | None:

        try:
            stmt = select(ModelAnswer).where(
                ModelAnswer.question_id == question_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ModelAnswerService] get_by_question error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> ModelAnswer | None:

        try:
            stmt = (
                select(ModelAnswer)
                .options(
                    selectinload(ModelAnswer.question)
                )
                .where(ModelAnswer.id == record_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ModelAnswerService] get_full error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        updates: dict,
    ) -> ModelAnswer:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("model answer not found")

            if "question_id" in updates:
                raise ValueError("question_id is immutable")

            if "answer_text" in updates:
                record.answer_text = str(updates["answer_text"])

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ModelAnswerService] update error: {e}",
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
                f"[ModelAnswerService] delete error: {e}",
                exc_info=True,
            )
            raise