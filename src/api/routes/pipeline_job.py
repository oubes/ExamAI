# ---- Imports ---- #
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.session import session_local

from src.services.pipeline_job.service import PipelineJobManagerService


# ---- Router ---- #
router = APIRouter()


# ---- Services ---- #
pipeline_job_service = PipelineJobManagerService()


# ---- DB Session ---- #
async def get_session():
    async with session_local() as session:
        yield session


# ---- Start Job ---- #
@router.post("/start")
async def start_job(
    subject_id: UUID,
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    job = await pipeline_job_service.start_job(
        session=session,
        subject_id=subject_id,
        book_id=book_id,
    )

    return job


# ---- Complete Job ---- #
@router.post("/{record_id}/complete")
async def complete_job(
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    job = await pipeline_job_service.complete_job(
        session=session,
        record_id=record_id,
    )

    return job


# ---- List Jobs ---- #
@router.get("/list")
async def list_jobs(
    subject_id: UUID | None = None,
    book_id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
):

    jobs = await pipeline_job_service.list_jobs(
        session=session,
        subject_id=subject_id,
        book_id=book_id,
    )

    return [
        {
            "id": str(job.id),
            "subject_id": str(job.subject_id),
            "book_id": str(job.book_id),
            "status": job.status,
            "current_chunk": job.current_chunk,
            "total_chunks": job.total_chunks,
        }
        for job in jobs
    ]

# ---- Fail Job ---- #
@router.post("/{record_id}/fail")
async def fail_job(
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    job = await pipeline_job_service.fail_job(
        session=session,
        record_id=record_id,
    )

    return job


# ---- Pause Job ---- #
@router.post("/{record_id}/pause")
async def pause_job(
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    job = await pipeline_job_service.pause_job(
        session=session,
        record_id=record_id,
    )

    return job


# ---- Resume Job ---- #
@router.post("/{record_id}/resume")
async def resume_job(
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    job = await pipeline_job_service.resume_job(
        session=session,
        record_id=record_id,
    )

    return job


# ---- Restart Job ---- #
@router.post("/{record_id}/restart")
async def restart_job(
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    job = await pipeline_job_service.restart_job(
        session=session,
        record_id=record_id,
    )

    return job


# ---- Progress % ---- #
@router.get("/{record_id}/progress")
async def get_progress(
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    percent = await pipeline_job_service.get_progress_percentage(
        session=session,
        record_id=record_id,
    )

    return {
        "progress": percent,
    }