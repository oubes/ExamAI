# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.questions.models.chunk import DocumentChunk
from src.domain.questions.services.pipeline_job import PipelineJobService


# ---- Dependencies ---- #
pipeline_job_service = PipelineJobService()

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

            # ---- STORE CONTEXT BEFORE DELETE ---- #
            subject_id = record.subject_id
            book_id = record.book_id

            await session.delete(record)
            await session.commit()

            # ---- DECREMENT PIPELINE PROGRESS ---- #
            job = await pipeline_job_service.get_by_subject_and_book(
                session=session,
                subject_id=subject_id,
                book_id=book_id,
            )

            if job and job.current_chunk > 0:
                await pipeline_job_service.update_progress(
                    session=session,
                    record_id=job.id,
                    current_chunk=job.current_chunk - 1,
                )

            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"[ChunkService] delete error: {e}", exc_info=True)
            raise
        
    # ---- Delete All By Subject + Book ---- #
    async def delete_all_by_subject_and_book(
        self,
        session: AsyncSession,
        subject_id: UUID,
        book_id: UUID,
    ) -> int:

        try:
            records = await self.list(
                session=session,
                limit=100000,
                offset=0,
            )

            filtered_records = [
                record
                for record in records
                if (
                    record.subject_id == subject_id
                    and record.book_id == book_id
                )
            ]

            if not filtered_records:
                return 0

            deleted_count = 0

            for record in filtered_records:
                deleted = await self.delete(
                    session=session,
                    record_id=record.id,
                )

                if deleted:
                    deleted_count += 1

            # ---- RESET PIPELINE JOB PROGRESS ---- #

            job = await pipeline_job_service.get_by_subject_and_book(
                session=session,
                subject_id=subject_id,
                book_id=book_id,
            )

            if job:
                await pipeline_job_service.update_progress(
                    session=session,
                    record_id=job.id,
                    current_chunk=0,
                )

            return deleted_count

        except Exception as e:
            logger.error(
                f"[ChunkService] delete_all_by_subject_and_book error: {e}",
                exc_info=True,
            )
            raise