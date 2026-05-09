# ---- Imports ---- #
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domain.education.models.chapter import Chapter


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Chapter Service ---- #
class ChapterService:

    # ---- Create Chapter ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Chapter:

        try:
            logger.debug(f"[ChapterService] create: {data}")

            record = Chapter(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[ChapterService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        chapter_id: int,
    ) -> Chapter | None:

        try:
            return await session.get(Chapter, chapter_id)

        except Exception as e:
            logger.error(f"[ChapterService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By Subject ---- #
    async def get_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Chapter]:

        try:
            stmt = (
                select(Chapter)
                .where(Chapter.subject_id == subject_id)
                .order_by(Chapter.order_index.asc())
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[ChapterService] get_by_subject error: {e}", exc_info=True)
            raise


    # ---- Update Chapter ---- #
    async def update(
        self,
        session: AsyncSession,
        chapter_id: int,
        updates: dict,
    ) -> Chapter:

        try:
            record = await session.get(Chapter, chapter_id)

            if not record:
                raise ValueError("chapter not found")

            # ---- protected fields ---- #
            protected = {"id", "subject_id"}

            for key, value in updates.items():
                if key in protected:
                    continue
                setattr(record, key, value)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[ChapterService] update error: {e}", exc_info=True)
            raise


    # ---- Delete Chapter ---- #
    async def delete(
        self,
        session: AsyncSession,
        chapter_id: int,
    ) -> bool:

        try:
            record = await session.get(Chapter, chapter_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[ChapterService] delete error: {e}", exc_info=True)
            raise


    # ---- Reorder Chapters ---- #
    async def reorder(
        self,
        session: AsyncSession,
        subject_id: int,
        ordered_ids: list[int],
    ) -> None:

        try:
            stmt = select(Chapter).where(
                Chapter.subject_id == subject_id
            )

            result = await session.execute(stmt)

            chapters = {c.id: c for c in result.scalars().all()}

            for index, chapter_id in enumerate(ordered_ids):
                if chapter_id in chapters:
                    chapters[chapter_id].order_index = index

            await session.commit()

        except Exception as e:
            logger.error(f"[ChapterService] reorder error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        subject_id: int,
    ) -> list[Chapter]:

        try:
            query = query.strip()

            if not query:
                return []

            stmt = select(Chapter).where(
                Chapter.title.ilike(f"%{query}%"),
                Chapter.subject_id == subject_id,
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[ChapterService] search error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> dict:

        try:
            stmt = select(func.count()).where(
                Chapter.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return {
                "total": result.scalar()
            }

        except Exception as e:
            logger.error(f"[ChapterService] stats error: {e}", exc_info=True)
            raise