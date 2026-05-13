# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.questions.models.chunk import DocumentChunk


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Chunk Service ---- #
class ChunkService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> DocumentChunk:

        try:
            record = DocumentChunk(
                book_id=payload["book_id"],
                subject_id=payload["subject_id"],
                chapter_id=payload.get("chapter_id"),
                topic_id=payload.get("topic_id"),
                chunk_index=payload["chunk_index"],
                content=payload["content"],
            )

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()
            logger.error(f"[ChunkService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> DocumentChunk | None:

        try:
            stmt = select(DocumentChunk).where(DocumentChunk.id == record_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[ChunkService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- List ---- #
    async def list(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DocumentChunk]:

        try:
            stmt = select(DocumentChunk).limit(limit).offset(offset)
            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[ChunkService] list error: {e}", exc_info=True)
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        updates: dict,
    ) -> DocumentChunk | None:

        try:
            record = await self.get_by_id(session, record_id)

            if not record:
                return None

            for key, value in updates.items():
                setattr(record, key, value)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()
            logger.error(f"[ChunkService] update error: {e}", exc_info=True)
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        try:
            record = await self.get_by_id(session, record_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"[ChunkService] delete error: {e}", exc_info=True)
            raise