# ---- Imports ---- #
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.domain.education.models.topic import Topic
from src.domain.education.models.chapter import Chapter


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Topic Service ---- #
class TopicService:

    # ---- Create Topic ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Topic:

        try:
            logger.debug(f"[TopicService] create: {data}")

            # ---- validate chapter-subject consistency ---- #
            stmt = select(Chapter).where(
                Chapter.id == data["chapter_id"],
                Chapter.subject_id == data["subject_id"],
            )

            result = await session.execute(stmt)
            chapter = result.scalar_one_or_none()

            if not chapter:
                raise ValueError("invalid chapter or subject mismatch")

            record = Topic(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[TopicService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        topic_id: int,
    ) -> Topic | None:

        try:
            return await session.get(Topic, topic_id)

        except Exception as e:
            logger.error(f"[TopicService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By Chapter ---- #
    async def get_by_chapter(
        self,
        session: AsyncSession,
        chapter_id: int,
    ) -> list[Topic]:

        try:
            stmt = select(Topic).where(
                Topic.chapter_id == chapter_id
            ).order_by(
                Topic.difficulty_weight.desc()
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[TopicService] get_by_chapter error: {e}", exc_info=True)
            raise


    # ---- Get By Subject ---- #
    async def get_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Topic]:

        try:
            stmt = select(Topic).where(
                Topic.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[TopicService] get_by_subject error: {e}", exc_info=True)
            raise


    # ---- Update Topic ---- #
    async def update(
        self,
        session: AsyncSession,
        topic_id: int,
        updates: dict,
    ) -> Topic:

        try:
            record = await session.get(Topic, topic_id)

            if not record:
                raise ValueError("topic not found")

            # ---- protected fields ---- #
            protected = {"id", "subject_id", "chapter_id"}

            # ---- optional consistency re-check ---- #
            if "chapter_id" in updates or "subject_id" in updates:
                stmt = select(Chapter).where(
                    Chapter.id == updates.get("chapter_id", record.chapter_id),
                    Chapter.subject_id == updates.get("subject_id", record.subject_id),
                )

                result = await session.execute(stmt)
                valid = result.scalar_one_or_none()

                if not valid:
                    raise ValueError("invalid chapter-subject relationship")

            for key, value in updates.items():
                if key in protected:
                    continue
                setattr(record, key, value)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[TopicService] update error: {e}", exc_info=True)
            raise


    # ---- Delete Topic ---- #
    async def delete(
        self,
        session: AsyncSession,
        topic_id: int,
    ) -> bool:

        try:
            record = await session.get(Topic, topic_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[TopicService] delete error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        subject_id: int | None = None,
        chapter_id: int | None = None,
    ) -> list[Topic]:

        try:
            query = query.strip()

            if not query:
                return []

            stmt = select(Topic).where(
                Topic.title.ilike(f"%{query}%")
            )

            if subject_id:
                stmt = stmt.where(Topic.subject_id == subject_id)

            if chapter_id:
                stmt = stmt.where(Topic.chapter_id == chapter_id)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[TopicService] search error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        chapter_id: int,
    ) -> dict:

        try:
            stmt = select(func.count()).where(
                Topic.chapter_id == chapter_id
            )

            result = await session.execute(stmt)

            return {
                "total": result.scalar()
            }

        except Exception as e:
            logger.error(f"[TopicService] stats error: {e}", exc_info=True)
            raise