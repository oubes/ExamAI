# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.education.models.subject import Subject
from src.domain.questions.models.pipeline_job import PipelineJob


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Pipeline Job Service ---- #
class PipelineJobService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> PipelineJob:

        try:
            book_id = payload["book_id"]
            subject_id = payload["subject_id"]

            subject_stmt = select(Subject.id).where(
                Subject.id == subject_id
            )

            subject_result = await session.execute(subject_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            record = PipelineJob(
                book_id=book_id,
                subject_id=subject_id,
                current_chunk=int(payload.get("current_chunk", 0)),
                total_chunks=int(payload.get("total_chunks", 0)),
                status=str(payload.get("status", "running")),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[PipelineJobService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[PipelineJobService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob | None:

        try:
            stmt = select(PipelineJob).where(
                PipelineJob.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[PipelineJobService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Progress ---- #
    async def update_progress(
        self,
        session: AsyncSession,
        record_id: UUID,
        current_chunk: int,
    ) -> PipelineJob:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if record is None:
                raise ValueError("pipeline job not found")

            record.current_chunk = int(current_chunk)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[PipelineJobService] update_progress error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Total Chunks (NEW) ---- #
    async def update_total_chunks(
        self,
        session: AsyncSession,
        record_id: UUID,
        total_chunks: int,
    ) -> PipelineJob:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if record is None:
                raise ValueError("pipeline job not found")

            record.total_chunks = int(total_chunks)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[PipelineJobService] update_total_chunks error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update Status ---- #
    async def update_status(
        self,
        session: AsyncSession,
        record_id: UUID,
        status: str,
    ) -> PipelineJob:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if record is None:
                raise ValueError("pipeline job not found")

            record.status = status

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[PipelineJobService] update_status error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Book ---- #
    async def list_by_book(
        self,
        session: AsyncSession,
        book_id: UUID,
    ) -> list[PipelineJob]:

        try:
            stmt = select(PipelineJob).where(
                PipelineJob.book_id == book_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[PipelineJobService] list_by_book error: {e}",
                exc_info=True,
            )
            raise


    # ---- Resume Info ---- #
    async def get_resume_state(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> tuple[int, int, str] | None:

        try:
            job = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if job is None:
                return None

            return (
                job.current_chunk,
                job.total_chunks,
                job.status,
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobService] get_resume_state error: {e}",
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

            if record is None:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[PipelineJobService] delete error: {e}",
                exc_info=True,
            )
            raise
        
    # ---- Get By Subject And Book ---- #
    async def get_by_subject_and_book(
        self,
        session: AsyncSession,
        subject_id: UUID,
        book_id: UUID,
    ) -> PipelineJob | None:

        try:
            stmt = select(PipelineJob).where(
                PipelineJob.subject_id == subject_id,
                PipelineJob.book_id == book_id,
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[PipelineJobService] get_by_subject_and_book error: {e}",
                exc_info=True,
            )
            raise