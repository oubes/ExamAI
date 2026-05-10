# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.attempts.models.attempt import ExamAttempt
from src.domain.education.models.exam import Exam
from src.domain.identity.models.user import User


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Exam Attempt Service ---- #
class ExamAttemptService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> ExamAttempt:

        try:
            exam_id = payload["exam_id"]
            user_id = payload["user_id"]

            exam_stmt = select(Exam.id).where(Exam.id == exam_id)
            user_stmt = select(User.id).where(User.id == user_id)

            exam_result = await session.execute(exam_stmt)
            user_result = await session.execute(user_stmt)

            if not exam_result.scalar_one_or_none():
                raise ValueError("exam not found")

            if not user_result.scalar_one_or_none():
                raise ValueError("user not found")

            record = ExamAttempt(
                exam_id=exam_id,
                user_id=user_id,
                final_score=float(payload.get("final_score", 0.0)),
                ai_score=float(payload.get("ai_score", 0.0)),
                human_score=float(payload.get("human_score", 0.0)),
                status=str(payload.get("status", "pending")),
                duration_sec=payload.get("duration_sec"),
                generation_mode=str(
                    payload.get("generation_mode", "manual")
                ),
                adaptive_session_id=payload.get(
                    "adaptive_session_id"
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[ExamAttemptService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ExamAttemptService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[ExamAttempt]:

        try:
            if not payloads:
                return []

            exam_ids = {p["exam_id"] for p in payloads}
            user_ids = {p["user_id"] for p in payloads}

            exam_stmt = select(Exam.id).where(
                Exam.id.in_(exam_ids)
            )

            user_stmt = select(User.id).where(
                User.id.in_(user_ids)
            )

            exam_result = await session.execute(exam_stmt)
            user_result = await session.execute(user_stmt)

            existing_exams = set(exam_result.scalars().all())
            existing_users = set(user_result.scalars().all())

            if exam_ids - existing_exams:
                raise ValueError("invalid exam_ids")

            if user_ids - existing_users:
                raise ValueError("invalid user_ids")

            records: list[ExamAttempt] = [
                ExamAttempt(
                    exam_id=p["exam_id"],
                    user_id=p["user_id"],
                    final_score=float(p.get("final_score", 0.0)),
                    ai_score=float(p.get("ai_score", 0.0)),
                    human_score=float(p.get("human_score", 0.0)),
                    status=str(p.get("status", "pending")),
                    duration_sec=p.get("duration_sec"),
                    generation_mode=str(
                        p.get("generation_mode", "manual")
                    ),
                    adaptive_session_id=p.get(
                        "adaptive_session_id"
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
                f"[ExamAttemptService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        attempt_id: UUID,
    ) -> bool:

        try:
            stmt = select(ExamAttempt.id).where(
                ExamAttempt.id == attempt_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[ExamAttemptService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        attempt_id: UUID,
    ) -> ExamAttempt | None:

        try:
            stmt = select(ExamAttempt).where(
                ExamAttempt.id == attempt_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ExamAttemptService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        attempt_id: UUID,
    ) -> ExamAttempt | None:

        try:
            stmt = (
                select(ExamAttempt)
                .options(
                    selectinload(ExamAttempt.answers),
                    selectinload(ExamAttempt.user),
                )
                .where(ExamAttempt.id == attempt_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ExamAttemptService] get_full error: {e}",
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
    ) -> list[ExamAttempt]:

        try:
            stmt = (
                select(ExamAttempt)
                .where(ExamAttempt.user_id == user_id)
                .order_by(ExamAttempt.completed_at.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ExamAttemptService] list_by_user error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By Exam ---- #
    async def list_by_exam(
        self,
        session: AsyncSession,
        exam_id: UUID,
    ) -> list[ExamAttempt]:

        try:
            stmt = (
                select(ExamAttempt)
                .where(ExamAttempt.exam_id == exam_id)
                .order_by(ExamAttempt.completed_at.desc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ExamAttemptService] list_by_exam error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Scores ---- #
    async def update_scores(
        self,
        session: AsyncSession,
        attempt_id: UUID,
        final_score: float | None = None,
        ai_score: float | None = None,
        human_score: float | None = None,
        status: str | None = None,
    ) -> ExamAttempt:

        try:
            record = await self.get_by_id(
                session=session,
                attempt_id=attempt_id,
            )

            if not record:
                raise ValueError("attempt not found")

            if final_score is not None:
                record.final_score = final_score

            if ai_score is not None:
                record.ai_score = ai_score

            if human_score is not None:
                record.human_score = human_score

            if status is not None:
                record.status = status

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ExamAttemptService] update_scores error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        attempt_id: UUID,
    ) -> bool:

        try:
            record = await self.get_by_id(
                session=session,
                attempt_id=attempt_id,
            )

            if not record:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ExamAttemptService] delete error: {e}",
                exc_info=True,
            )
            raise