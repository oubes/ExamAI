# ---- Imports ---- #
import logging
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.adaptive_exam.models.generated_exam_session import GeneratedExamSession
from src.domain.identity.models.user import User
from src.domain.education.models.subject import Subject


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Generated Exam Session Service ---- #
class GeneratedExamSessionService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> GeneratedExamSession:

        try:
            user_id = payload["user_id"]
            subject_id = payload["subject_id"]

            user_stmt = select(User.id).where(User.id == user_id)
            subject_stmt = select(Subject.id).where(Subject.id == subject_id)

            user_result = await session.execute(user_stmt)
            subject_result = await session.execute(subject_stmt)

            if not user_result.scalar_one_or_none():
                raise ValueError("user not found")

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            record = GeneratedExamSession(
                user_id=user_id,
                subject_id=subject_id,
                target_difficulty=float(
                    payload.get("target_difficulty", 1.0)
                ),
                generation_strategy=str(
                    payload.get("generation_strategy", "adaptive")
                ),
                estimated_mastery=float(
                    payload.get("estimated_mastery", 0.0)
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamSessionService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamSessionService] create error: {e}",
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
            stmt = select(GeneratedExamSession.id).where(
                GeneratedExamSession.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[GeneratedExamSessionService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> GeneratedExamSession | None:

        try:
            stmt = select(GeneratedExamSession).where(
                GeneratedExamSession.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[GeneratedExamSessionService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> GeneratedExamSession | None:

        try:
            stmt = (
                select(GeneratedExamSession)
                .options(
                    selectinload(GeneratedExamSession.questions)
                )
                .where(GeneratedExamSession.id == record_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[GeneratedExamSessionService] get_full error: {e}",
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
    ) -> list[GeneratedExamSession]:

        try:
            stmt = (
                select(GeneratedExamSession)
                .where(GeneratedExamSession.user_id == user_id)
                .order_by(GeneratedExamSession.started_at.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[GeneratedExamSessionService] list_by_user error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> list[GeneratedExamSession]:

        try:
            stmt = (
                select(GeneratedExamSession)
                .where(GeneratedExamSession.subject_id == subject_id)
                .order_by(GeneratedExamSession.started_at.desc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[GeneratedExamSessionService] list_by_subject error: {e}",
                exc_info=True,
            )
            raise


    # ---- Mark Completed ---- #
    async def mark_completed(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> GeneratedExamSession:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("session not found")

            record.completed_at = datetime.now(timezone.utc) # type: ignore

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamSessionService] mark_completed error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Metrics ---- #
    async def update_metrics(
        self,
        session: AsyncSession,
        record_id: UUID,
        estimated_mastery: float | None = None,
        target_difficulty: float | None = None,
    ) -> GeneratedExamSession:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("session not found")

            if estimated_mastery is not None:
                record.estimated_mastery = estimated_mastery

            if target_difficulty is not None:
                record.target_difficulty = target_difficulty

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[GeneratedExamSessionService] update_metrics error: {e}",
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
                f"[GeneratedExamSessionService] delete error: {e}",
                exc_info=True,
            )
            raise