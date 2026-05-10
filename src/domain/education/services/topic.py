# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import func, select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.education.models.topic import Topic
from src.domain.education.models.subject import Subject
from src.domain.education.models.chapter import Chapter
from src.domain.questions.models.question import Question
from src.domain.education.models.skill import Skill


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Topic Service ---- #
class TopicService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> Topic:

        try:
            subject_id = payload["subject_id"]
            chapter_id = payload["chapter_id"]

            subject_stmt = select(Subject.id).where(
                Subject.id == subject_id
            )

            chapter_stmt = select(Chapter.id).where(
                Chapter.id == chapter_id
            )

            subject_result = await session.execute(subject_stmt)
            chapter_result = await session.execute(chapter_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            if not chapter_result.scalar_one_or_none():
                raise ValueError("chapter not found")

            record = Topic(
                subject_id=subject_id,
                chapter_id=chapter_id,
                title=str(payload["title"]).strip(),
                description=payload.get("description"),
                difficulty_weight=float(
                    payload.get("difficulty_weight", 1.0)
                ),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[TopicService] create integrity error: {e}",
                exc_info=True,
            )

            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[TopicService] create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Topic]:

        try:
            if not payloads:
                return []

            subject_ids = {p["subject_id"] for p in payloads}
            chapter_ids = {p["chapter_id"] for p in payloads}

            subject_stmt = select(Subject.id).where(
                Subject.id.in_(subject_ids)
            )

            chapter_stmt = select(Chapter.id).where(
                Chapter.id.in_(chapter_ids)
            )

            subject_result = await session.execute(subject_stmt)
            chapter_result = await session.execute(chapter_stmt)

            existing_subjects = set(subject_result.scalars().all())
            existing_chapters = set(chapter_result.scalars().all())

            missing_subjects = subject_ids - existing_subjects
            missing_chapters = chapter_ids - existing_chapters

            if missing_subjects:
                raise ValueError(f"subjects not found: {missing_subjects}")

            if missing_chapters:
                raise ValueError(f"chapters not found: {missing_chapters}")

            records: list[Topic] = []

            for p in payloads:
                records.append(
                    Topic(
                        subject_id=p["subject_id"],
                        chapter_id=p["chapter_id"],
                        title=str(p["title"]).strip(),
                        description=p.get("description"),
                        difficulty_weight=float(
                            p.get("difficulty_weight", 1.0)
                        ),
                    )
                )

            session.add_all(records)

            await session.commit()

            for r in records:
                await session.refresh(r)

            return records

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[TopicService] bulk_create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> bool:

        try:
            stmt = select(Topic.id).where(
                Topic.id == topic_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[TopicService] exists error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> Topic | None:

        try:
            stmt = select(Topic).where(
                Topic.id == topic_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[TopicService] get_by_id error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> Topic | None:

        try:
            stmt = (
                select(Topic)
                .options(
                    selectinload(Topic.subject),
                    selectinload(Topic.chapter),
                    selectinload(Topic.skills),
                    selectinload(Topic.questions),
                )
                .where(Topic.id == topic_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[TopicService] get_full error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Many By IDs ---- #
    async def get_many_by_ids(
        self,
        session: AsyncSession,
        topic_ids: list[UUID],
    ) -> list[Topic]:

        try:
            if not topic_ids:
                return []

            stmt = select(Topic).where(
                Topic.id.in_(topic_ids)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[TopicService] get_many_by_ids error: {e}",
                exc_info=True,
            )

            raise


    # ---- List ---- #
    async def list_topics(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Topic]:

        try:
            stmt = (
                select(Topic)
                .order_by(Topic.title.asc())
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[TopicService] list_topics error: {e}",
                exc_info=True,
            )

            raise


    # ---- List By Chapter ---- #
    async def list_by_chapter(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> list[Topic]:

        try:
            stmt = (
                select(Topic)
                .where(Topic.chapter_id == chapter_id)
                .order_by(Topic.title.asc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[TopicService] list_by_chapter error: {e}",
                exc_info=True,
            )

            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Topic]:

        try:
            q = query.strip()

            stmt = (
                select(Topic)
                .where(
                    Topic.title.ilike(f"%{q}%")
                    | Topic.description.ilike(f"%{q}%")
                )
                .order_by(Topic.title.asc())
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[TopicService] search error: {e}",
                exc_info=True,
            )

            raise


    # ---- Count ---- #
    async def count(
        self,
        session: AsyncSession,
    ) -> int:

        try:
            stmt = select(func.count(Topic.id))

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[TopicService] count error: {e}",
                exc_info=True,
            )

            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        topic_id: UUID,
        updates: dict,
    ) -> Topic:

        try:
            record = await self.get_by_id(
                session=session,
                topic_id=topic_id,
            )

            if not record:
                raise ValueError("topic not found")

            if "subject_id" in updates:
                subject_stmt = select(Subject.id).where(
                    Subject.id == updates["subject_id"]
                )

                subject_result = await session.execute(subject_stmt)

                if not subject_result.scalar_one_or_none():
                    raise ValueError("subject not found")

            if "chapter_id" in updates:
                chapter_stmt = select(Chapter.id).where(
                    Chapter.id == updates["chapter_id"]
                )

                chapter_result = await session.execute(chapter_stmt)

                if not chapter_result.scalar_one_or_none():
                    raise ValueError("chapter not found")

            for k, v in updates.items():
                if k == "id":
                    continue

                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[TopicService] update error: {e}",
                exc_info=True,
            )

            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> bool:

        try:
            record = await self.get_full(
                session=session,
                topic_id=topic_id,
            )

            if not record:
                return False

            if record.questions:
                raise ValueError("cannot delete topic with questions")

            if record.skills:
                raise ValueError("cannot delete topic with skills")

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[TopicService] delete error: {e}",
                exc_info=True,
            )

            raise


    # ---- Hard Delete ---- #
    async def hard_delete(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Topic).where(
                Topic.id == topic_id
            )

            result = await session.execute(stmt)

            await session.commit()

            affected = result.rowcount # type: ignore

            return bool(affected and affected > 0)

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[TopicService] hard_delete error: {e}",
                exc_info=True,
            )

            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> dict:

        try:
            questions_stmt = select(
                func.count(Question.id)
            ).where(
                Question.topic_id == topic_id
            )

            skills_stmt = select(
                func.count(Skill.id)
            ).where(
                Skill.topic_id == topic_id
            )

            questions_result = await session.execute(
                questions_stmt
            )

            skills_result = await session.execute(skills_stmt)

            return {
                "questions": int(questions_result.scalar() or 0),
                "skills": int(skills_result.scalar() or 0),
            }

        except Exception as e:
            logger.error(
                f"[TopicService] stats error: {e}",
                exc_info=True,
            )

            raise