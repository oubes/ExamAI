# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.questions.models.pipeline_job import PipelineJob

from src.domain.questions.services.pipeline_job import (
    PipelineJobService,
)


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Services ---- #
pipeline_job_service = PipelineJobService()


# ---- Pipeline Job Manager Service ---- #
class PipelineJobManagerService:

    # ---- Start Job ---- #
    async def start_job(
        self,
        session: AsyncSession,
        subject_id: UUID,
        book_id: UUID,
    ) -> PipelineJob:

        try:

            existing = await pipeline_job_service.get_by_subject_and_book(
                session=session,
                subject_id=subject_id,
                book_id=book_id,
            )

            if existing:
                return existing

            return await pipeline_job_service.create(
                session=session,
                payload={
                    "book_id": book_id,
                    "subject_id": subject_id,
                    "status": "running",
                    "current_chunk": 0,
                    "total_chunks": 0,
                },
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] start_job error: {e}",
                exc_info=True,
            )
            raise

    # ---- Complete Job ---- #
    async def complete_job(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob:

        try:

            job = await pipeline_job_service.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not job:
                raise ValueError("pipeline job not found")

            await pipeline_job_service.update_progress(
                session=session,
                record_id=record_id,
                current_chunk=job.total_chunks,
            )

            return await pipeline_job_service.update_status(
                session=session,
                record_id=record_id,
                status="completed",
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] complete_job error: {e}",
                exc_info=True,
            )
            raise

    # ---- Fail Job ---- #
    async def fail_job(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob:

        try:

            return await pipeline_job_service.update_status(
                session=session,
                record_id=record_id,
                status="failed",
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] fail_job error: {e}",
                exc_info=True,
            )
            raise

    # ---- Pause Job ---- #
    async def pause_job(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob:

        try:

            return await pipeline_job_service.update_status(
                session=session,
                record_id=record_id,
                status="paused",
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] pause_job error: {e}",
                exc_info=True,
            )
            raise

    # ---- Resume Job ---- #
    async def resume_job(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob:

        try:

            return await pipeline_job_service.update_status(
                session=session,
                record_id=record_id,
                status="running",
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] resume_job error: {e}",
                exc_info=True,
            )
            raise

    # ---- Restart Job ---- #
    async def restart_job(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob:

        try:

            await pipeline_job_service.update_progress(
                session=session,
                record_id=record_id,
                current_chunk=0,
            )

            return await pipeline_job_service.update_status(
                session=session,
                record_id=record_id,
                status="running",
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] restart_job error: {e}",
                exc_info=True,
            )
            raise

    # ---- Advance Chunk ---- #
    async def advance_chunk(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> PipelineJob:

        try:

            job = await pipeline_job_service.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not job:
                raise ValueError("pipeline job not found")

            return await pipeline_job_service.update_progress(
                session=session,
                record_id=record_id,
                current_chunk=job.current_chunk + 1,
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] advance_chunk error: {e}",
                exc_info=True,
            )
            raise

    # ---- Get Progress Percentage ---- #
    async def get_progress_percentage(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> float:

        try:

            job = await pipeline_job_service.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not job:
                raise ValueError("pipeline job not found")

            if job.total_chunks <= 0:
                return 0.0

            return round(
                (job.current_chunk / job.total_chunks) * 100,
                2,
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] get_progress_percentage error: {e}",
                exc_info=True,
            )
            raise
        
    # ---- List Jobs ---- #
    async def list_jobs(
        self,
        session: AsyncSession,
        subject_id: UUID | None = None,
        book_id: UUID | None = None,
    ) -> list[PipelineJob]:

        try:

            # ---- USE DOMAIN SERVICE ---- #
            if subject_id and book_id:
                job = await pipeline_job_service.get_by_subject_and_book(
                    session=session,
                    subject_id=subject_id,
                    book_id=book_id,
                )
                return [job] if job else []

            # ---- FALLBACK: LIST ALL BY BOOK ---- #
            if book_id and not subject_id:
                return await pipeline_job_service.list_by_book(
                    session=session,
                    book_id=book_id,
                )

            # ---- FALLBACK: EMPTY SUBJECT FILTER ONLY ---- #
            if subject_id and not book_id:
                # no direct method in domain service → safe fallback via scan
                jobs = await pipeline_job_service.list_by_book(
                    session=session,
                    book_id=book_id,  # intentionally None-safe handled by service layer
                )
                return [
                    j for j in jobs
                    if j.subject_id == subject_id
                ]

            # ---- DEFAULT: ALL JOBS ---- #
            return await pipeline_job_service.list_by_book(
                session=session,
                book_id=book_id if book_id else UUID(int=0),  # safe guard (avoid accidental full scan)
            )

        except Exception as e:
            logger.error(
                f"[PipelineJobManagerService] list_jobs error: {e}",
                exc_info=True,
            )
            raise