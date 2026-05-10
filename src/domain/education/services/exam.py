# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.education.models.exam import Exam
from src.domain.education.models.subject import Subject
from src.domain.questions.models.question import Question


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Exam Service ---- #
class ExamService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> Exam:

        try:
            subject_id = payload["subject_id"]

            subject_stmt = select(Subject.id).where(
                Subject.id == subject_id
            )

            subject_result = await session.execute(subject_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            record = Exam(
                subject_id=subject_id,
                title=str(payload["title"]).strip(),
                exam_type=str(
                    payload.get("exam_type", "static")
                ).strip(),
                difficulty_profile=float(
                    payload.get("difficulty_profile", 1.0)
                ),
                time_limit=int(payload.get("time_limit", 0)),
                scope_config=payload.get("scope_config"),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[ExamService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ExamService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Exam]:

        try:
            if not payloads:
                return []

            subject_ids = {p["subject_id"] for p in payloads}

            subject_stmt = select(Subject.id).where(
                Subject.id.in_(subject_ids)
            )

            subject_result = await session.execute(subject_stmt)

            existing_subjects = set(
                subject_result.scalars().all()
            )

            if subject_ids - existing_subjects:
                raise ValueError("invalid subject_ids")

            records = [
                Exam(
                    subject_id=p["subject_id"],
                    title=str(p["title"]).strip(),
                    exam_type=str(p.get("exam_type", "static")).strip(),
                    difficulty_profile=float(
                        p.get("difficulty_profile", 1.0)
                    ),
                    time_limit=int(p.get("time_limit", 0)),
                    scope_config=p.get("scope_config"),
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
                f"[ExamService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        exam_id: UUID,
    ) -> bool:

        try:
            stmt = select(Exam.id).where(Exam.id == exam_id)

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[ExamService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        exam_id: UUID,
    ) -> Exam | None:

        try:
            stmt = select(Exam).where(Exam.id == exam_id)

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ExamService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        exam_id: UUID,
    ) -> Exam | None:

        try:
            stmt = (
                select(Exam)
                .options(
                    selectinload(Exam.subject),
                    selectinload(Exam.questions),
                )
                .where(Exam.id == exam_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ExamService] get_full error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Many ---- #
    async def get_many_by_ids(
        self,
        session: AsyncSession,
        exam_ids: list[UUID],
    ) -> list[Exam]:

        try:
            if not exam_ids:
                return []

            stmt = select(Exam).where(Exam.id.in_(exam_ids))

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ExamService] get_many_by_ids error: {e}",
                exc_info=True,
            )
            raise


    # ---- List ---- #
    async def list_exams(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Exam]:

        try:
            stmt = (
                select(Exam)
                .order_by(Exam.title.asc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ExamService] list_exams error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> list[Exam]:

        try:
            stmt = (
                select(Exam)
                .where(Exam.subject_id == subject_id)
                .order_by(Exam.created_at.desc()) # type: ignore
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ExamService] list_by_subject error: {e}",
                exc_info=True,
            )
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Exam]:

        try:
            q = query.strip()

            stmt = (
                select(Exam)
                .where(
                    Exam.title.ilike(f"%{q}%")
                    | Exam.exam_type.ilike(f"%{q}%")
                )
                .order_by(Exam.created_at.desc()) # type: ignore
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ExamService] search error: {e}",
                exc_info=True,
            )
            raise


    # ---- Count ---- #
    async def count(
        self,
        session: AsyncSession,
    ) -> int:

        try:
            stmt = select(func.count(Exam.id))

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[ExamService] count error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        exam_id: UUID,
    ) -> bool:

        try:
            record = await self.get_full(
                session=session,
                exam_id=exam_id,
            )

            if not record:
                return False

            if record.questions:
                raise ValueError("cannot delete exam with questions")

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ExamService] delete error: {e}",
                exc_info=True,
            )
            raise


    # ---- Hard Delete ---- #
    async def hard_delete(
        self,
        session: AsyncSession,
        exam_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Exam).where(Exam.id == exam_id)

            result = await session.execute(stmt)

            await session.commit()

            affected = result.rowcount # type: ignore

            return bool(affected and affected > 0)

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ExamService] hard_delete error: {e}",
                exc_info=True,
            )
            raise