# ---- Imports ---- #
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.education.services.topic import TopicService as TopicRepoService


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Services ---- #
topic_service = TopicRepoService()


# ---- Education Service ---- #
class TopicService:

    # ---- Add Topic ---- #
    async def add_topic(
        self,
        session: AsyncSession,
        payload: dict,
    ):
        try:
            record = await topic_service.create(
                session=session,
                data=payload,
            )

            return self._format_topic(record)

        except Exception as e:
            logger.error(
                f"[EducationService] add_topic error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Topic ---- #
    async def get_topic(
        self,
        session: AsyncSession,
        topic_id,
    ):
        try:
            record = await topic_service.get_by_id(
                session=session,
                topic_id=topic_id,
            )

            if not record:
                raise ValueError("topic not found")

            return self._format_topic(record)

        except Exception as e:
            logger.error(
                f"[EducationService] get_topic error: {e}",
                exc_info=True,
            )
            raise


    # ---- List Topics ---- #
    async def list_topics(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ):
        try:
            records = await topic_service.list_topics(
                session=session,
                limit=limit,
                offset=offset,
            )

            return [
                self._format_topic(record)
                for record in records
            ]

        except Exception as e:
            logger.error(
                f"[EducationService] list_topics error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Topic ---- #
    async def update_topic(
        self,
        session: AsyncSession,
        topic_id,
        updates: dict,
    ):
        try:
            record = await topic_service.update(
                session=session,
                topic_id=topic_id,
                updates=updates,
            )

            return self._format_topic(record)

        except Exception as e:
            logger.error(
                f"[EducationService] update_topic error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete Topic ---- #
    async def delete_topic(
        self,
        session: AsyncSession,
        topic_id,
    ) -> bool:
        try:
            deleted = await topic_service.delete(
                session=session,
                topic_id=topic_id,
            )

            if not deleted:
                raise ValueError("topic not found")

            return deleted

        except Exception as e:
            logger.error(
                f"[EducationService] delete_topic error: {e}",
                exc_info=True,
            )
            raise


    # ---- Hard Delete Topic ---- #
    async def hard_delete_topic(
        self,
        session: AsyncSession,
        topic_id,
    ) -> bool:
        try:
            deleted = await topic_service.hard_delete(
                session=session,
                topic_id=topic_id,
            )

            if not deleted:
                raise ValueError("topic not found")

            return deleted

        except Exception as e:
            logger.error(
                f"[EducationService] hard_delete_topic error: {e}",
                exc_info=True,
            )
            raise


    # ---- Formatter ---- #
    def _format_topic(self, record):
        return {
            "id": record.id,
            "subject_id": record.subject_id,
            "chapter_id": record.chapter_id,
            "title": record.title,
            "description": record.description,
            "difficulty_weight": record.difficulty_weight,
        }