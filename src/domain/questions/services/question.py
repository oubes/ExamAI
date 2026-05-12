# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.questions.models.question import Question
from src.domain.education.models.subject import Subject
from src.domain.education.models.chapter import Chapter
from src.domain.education.models.topic import Topic


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Question Service ---- #
class QuestionService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> Question:

        try:
            subject_id = payload["subject_id"]
            chapter_id = payload["chapter_id"]
            topic_id = payload["topic_id"]

            subject_stmt = select(Subject.id).where(
                Subject.id == subject_id
            )
            chapter_stmt = select(Chapter.id).where(
                Chapter.id == chapter_id
            )
            topic_stmt = select(Topic.id).where(
                Topic.id == topic_id
            )

            subject_result = await session.execute(subject_stmt)
            chapter_result = await session.execute(chapter_stmt)
            topic_result = await session.execute(topic_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            if not chapter_result.scalar_one_or_none():
                raise ValueError("chapter not found")

            if not topic_result.scalar_one_or_none():
                raise ValueError("topic not found")

            record = Question(
                subject_id=subject_id,
                chapter_id=chapter_id,
                topic_id=topic_id,
                content=str(payload["content"]),
                explanation=payload.get("explanation"),
                type=str(payload["type"]),
                difficulty=int(payload.get("difficulty", 1)),
                importance=int(payload.get("importance", 1)),
                tags=payload.get("tags"),
                # embedding=payload["embedding"],
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[QuestionService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Question]:

        try:
            if not payloads:
                return []

            subject_ids = {p["subject_id"] for p in payloads}
            chapter_ids = {p["chapter_id"] for p in payloads}
            topic_ids = {p["topic_id"] for p in payloads}

            subject_stmt = select(Subject.id).where(Subject.id.in_(subject_ids))
            chapter_stmt = select(Chapter.id).where(Chapter.id.in_(chapter_ids))
            topic_stmt = select(Topic.id).where(Topic.id.in_(topic_ids))

            subject_result = await session.execute(subject_stmt)
            chapter_result = await session.execute(chapter_stmt)
            topic_result = await session.execute(topic_stmt)

            if subject_ids - set(subject_result.scalars().all()):
                raise ValueError("invalid subject_ids")

            if chapter_ids - set(chapter_result.scalars().all()):
                raise ValueError("invalid chapter_ids")

            if topic_ids - set(topic_result.scalars().all()):
                raise ValueError("invalid topic_ids")

            records: list[Question] = [
                Question(
                    subject_id=p["subject_id"],
                    chapter_id=p["chapter_id"],
                    topic_id=p["topic_id"],
                    content=str(p["content"]),
                    explanation=p.get("explanation"),
                    type=str(p["type"]),
                    difficulty=int(p.get("difficulty", 1)),
                    importance=int(p.get("importance", 1)),
                    tags=p.get("tags"),
                    # embedding=p["embedding"],
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
                f"[QuestionService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> Question | None:

        try:
            stmt = select(Question).where(
                Question.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[QuestionService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> Question | None:

        try:
            stmt = (
                select(Question)
                .options(
                    selectinload(Question.options),
                    selectinload(Question.model_answer),
                    selectinload(Question.skill_links),
                )
                .where(Question.id == record_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[QuestionService] get_full error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Filters ---- #
    async def list_by_filters(
        self,
        session: AsyncSession,
        subject_id: UUID | None = None,
        chapter_id: UUID | None = None,
        topic_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Question]:

        try:
            stmt = select(Question)

            if subject_id:
                stmt = stmt.where(Question.subject_id == subject_id)

            if chapter_id:
                stmt = stmt.where(Question.chapter_id == chapter_id)

            if topic_id:
                stmt = stmt.where(Question.topic_id == topic_id)

            stmt = stmt.limit(limit).offset(offset)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[QuestionService] list_by_filters error: {e}",
                exc_info=True,
            )
            raise


    # ---- Search Text ---- #
    async def search_text(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Question]:

        try:
            stmt = (
                select(Question)
                .where(Question.content.ilike(f"%{query}%"))
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[QuestionService] search_text error: {e}",
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
                f"[QuestionService] delete error: {e}",
                exc_info=True,
            )
            raise