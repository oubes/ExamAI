# ---- Imports ---- #
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.education.services.chapter import ChapterService as ChapterRepoService


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Services ---- #
chapter_service = ChapterRepoService()


# ---- Education Service ---- #
class ChapterService:

    # ---- Add Chapter ---- #
    async def add_chapter(
        self,
        session: AsyncSession,
        payload: dict,
    ):
        try:
            record = await chapter_service.create(
                session=session,
                data=payload,
            )

            return self._format_chapter(record)

        except Exception as e:
            logger.error(
                f"[EducationService] add_chapter error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get Chapter ---- #
    async def get_chapter(
        self,
        session: AsyncSession,
        chapter_id,
    ):
        try:
            record = await chapter_service.get_by_id(
                session=session,
                chapter_id=chapter_id,
            )

            if not record:
                raise ValueError("chapter not found")

            return self._format_chapter(record)

        except Exception as e:
            logger.error(
                f"[EducationService] get_chapter error: {e}",
                exc_info=True,
            )
            raise


    # ---- List Chapters ---- #
    async def list_chapters(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ):
        try:
            records = await chapter_service.list_chapters(
                session=session,
                limit=limit,
                offset=offset,
            )

            return [
                self._format_chapter(record)
                for record in records
            ]

        except Exception as e:
            logger.error(
                f"[EducationService] list_chapters error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Chapter ---- #
    async def update_chapter(
        self,
        session: AsyncSession,
        chapter_id,
        updates: dict,
    ):
        try:
            record = await chapter_service.update(
                session=session,
                chapter_id=chapter_id,
                updates=updates,
            )

            return self._format_chapter(record)

        except Exception as e:
            logger.error(
                f"[EducationService] update_chapter error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete Chapter ---- #
    async def delete_chapter(
        self,
        session: AsyncSession,
        chapter_id,
    ) -> bool:
        try:
            deleted = await chapter_service.delete(
                session=session,
                chapter_id=chapter_id,
            )

            if not deleted:
                raise ValueError("chapter not found")

            return deleted

        except Exception as e:
            logger.error(
                f"[EducationService] delete_chapter error: {e}",
                exc_info=True,
            )
            raise


    # ---- Hard Delete Chapter ---- #
    async def hard_delete_chapter(
        self,
        session: AsyncSession,
        chapter_id,
    ) -> bool:
        try:
            deleted = await chapter_service.hard_delete(
                session=session,
                chapter_id=chapter_id,
            )

            if not deleted:
                raise ValueError("chapter not found")

            return deleted

        except Exception as e:
            logger.error(
                f"[EducationService] hard_delete_chapter error: {e}",
                exc_info=True,
            )
            raise


    # ---- Formatter ---- #
    def _format_chapter(self, record):
        return {
            "id": record.id,
            "subject_id": record.subject_id,
            "title": record.title,
            "description": record.description,
            "order_index": record.order_index,
        }