# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.attempts.models.feedback import Feedback
from src.domain.attempts.models.answer import Answer


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Feedback Service ---- #
class FeedbackService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> Feedback:

        try:
            answer_id = payload["answer_id"]

            answer_stmt = select(Answer.id).where(
                Answer.id == answer_id
            )

            answer_result = await session.execute(answer_stmt)

            if not answer_result.scalar_one_or_none():
                raise ValueError("answer not found")

            record = Feedback(
                answer_id=answer_id,
                feedback_text=str(payload["feedback_text"]),
                reasoning=payload.get("reasoning"),
                quality_score=float(
                    payload.get("quality_score", 0.0)
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[FeedbackService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[FeedbackService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Feedback]:

        try:
            if not payloads:
                return []

            answer_ids = {p["answer_id"] for p in payloads}

            answer_stmt = select(Answer.id).where(
                Answer.id.in_(answer_ids)
            )

            answer_result = await session.execute(answer_stmt)

            existing_answers = set(
                answer_result.scalars().all()
            )

            if answer_ids - existing_answers:
                raise ValueError("invalid answer_ids")

            records: list[Feedback] = [
                Feedback(
                    answer_id=p["answer_id"],
                    feedback_text=str(p["feedback_text"]),
                    reasoning=p.get("reasoning"),
                    quality_score=float(
                        p.get("quality_score", 0.0)
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
                f"[FeedbackService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        feedback_id: UUID,
    ) -> bool:

        try:
            stmt = select(Feedback.id).where(
                Feedback.id == feedback_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[FeedbackService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        feedback_id: UUID,
    ) -> Feedback | None:

        try:
            stmt = select(Feedback).where(
                Feedback.id == feedback_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[FeedbackService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        feedback_id: UUID,
    ) -> Feedback | None:

        try:
            stmt = (
                select(Feedback)
                .options(
                    selectinload(Feedback.answer)
                )
                .where(Feedback.id == feedback_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[FeedbackService] get_full error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Answer ---- #
    async def get_by_answer(
        self,
        session: AsyncSession,
        answer_id: UUID,
    ) -> Feedback | None:

        try:
            stmt = select(Feedback).where(
                Feedback.answer_id == answer_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[FeedbackService] get_by_answer error: {e}",
                exc_info=True,
            )
            raise


    # ---- List ---- #
    async def list_feedback(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Feedback]:

        try:
            stmt = (
                select(Feedback)
                .order_by(Feedback.quality_score.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[FeedbackService] list_feedback error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        feedback_id: UUID,
        updates: dict,
    ) -> Feedback:

        try:
            record = await self.get_by_id(
                session=session,
                feedback_id=feedback_id,
            )

            if not record:
                raise ValueError("feedback not found")

            if "answer_id" in updates:
                raise ValueError("answer_id is immutable")

            for k, v in updates.items():
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[FeedbackService] update error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        feedback_id: UUID,
    ) -> bool:

        try:
            record = await self.get_by_id(
                session=session,
                feedback_id=feedback_id,
            )

            if not record:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[FeedbackService] delete error: {e}",
                exc_info=True,
            )
            raise