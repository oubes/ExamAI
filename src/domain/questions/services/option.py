# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.questions.models.option import QuestionOption
from src.domain.questions.models.question import Question


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Question Option Service ---- #
class QuestionOptionService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> QuestionOption:

        try:
            question_id = payload["question_id"]

            question_stmt = select(Question.id).where(
                Question.id == question_id
            )

            question_result = await session.execute(question_stmt)

            if not question_result.scalar_one_or_none():
                raise ValueError("question not found")

            record = QuestionOption(
                question_id=question_id,
                option_text=str(payload["option_text"]),
                is_correct=bool(payload.get("is_correct", False)),
                order=int(payload.get("order", 0)),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[QuestionOptionService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionOptionService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[QuestionOption]:

        try:
            if not payloads:
                return []

            question_ids = {p["question_id"] for p in payloads}

            question_stmt = select(Question.id).where(
                Question.id.in_(question_ids)
            )

            question_result = await session.execute(question_stmt)

            existing_questions = set(
                question_result.scalars().all()
            )

            if question_ids - existing_questions:
                raise ValueError("invalid question_ids")

            records: list[QuestionOption] = [
                QuestionOption(
                    question_id=p["question_id"],
                    option_text=str(p["option_text"]),
                    is_correct=bool(p.get("is_correct", False)),
                    order=int(p.get("order", 0)),
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
                f"[QuestionOptionService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> QuestionOption | None:

        try:
            stmt = select(QuestionOption).where(
                QuestionOption.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[QuestionOptionService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Question ---- #
    async def list_by_question(
        self,
        session: AsyncSession,
        question_id: UUID,
    ) -> list[QuestionOption]:

        try:
            stmt = (
                select(QuestionOption)
                .where(QuestionOption.question_id == question_id)
                .order_by(QuestionOption.order.asc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[QuestionOptionService] list_by_question error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        updates: dict,
    ) -> QuestionOption:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("question option not found")

            if "question_id" in updates:
                raise ValueError("question_id is immutable")

            if "option_text" in updates:
                record.option_text = str(updates["option_text"])

            if "is_correct" in updates:
                record.is_correct = bool(updates["is_correct"])

            if "order" in updates:
                record.order = int(updates["order"])

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionOptionService] update error: {e}",
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
                f"[QuestionOptionService] delete error: {e}",
                exc_info=True,
            )
            raise