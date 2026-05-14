# ---- Imports ---- #
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.db import get_session
from src.auth.roles import admin_required

from src.services.question.chunk_service import ChunkService

from src.api.models.chunk_models import (
    CreateChunkRequest,
    ChunkResponse,
    ListChunksResponse,
    UpdateChunkRequest,
    DeleteChunkResponse,
)


# ---- Router ---- #
router = APIRouter()

# ---- Service ---- #
chunk_service = ChunkService()


# ---- Create Chunk ---- #
@router.post("", response_model=ChunkResponse)
async def create_chunk(
    payload: CreateChunkRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
):
    try:
        record = await chunk_service.create(
            session=session,
            payload=payload.model_dump(),
        )

        return ChunkResponse(**record.__dict__)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Get Chunk ---- #
@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
):
    try:
        record = await chunk_service.get_by_id(
            session=session,
            record_id=chunk_id,
        )

        if not record:
            raise HTTPException(status_code=404, detail="not found")

        return ChunkResponse(**record.__dict__)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- List Chunks ---- #
@router.get("", response_model=ListChunksResponse)
async def list_chunks(
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
):
    try:
        records = await chunk_service.list(
            session=session,
        )

        return ListChunksResponse(
            items=[ChunkResponse(**r.__dict__) for r in records]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Update Chunk ---- #
@router.put("/{chunk_id}", response_model=ChunkResponse)
async def update_chunk(
    chunk_id: UUID,
    payload: UpdateChunkRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
):
    try:
        record = await chunk_service.update(
            session=session,
            record_id=chunk_id,
            updates=payload.model_dump(exclude_none=True),
        )

        if not record:
            raise HTTPException(status_code=404, detail="not found")

        return ChunkResponse(**record.__dict__)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Delete Chunk ---- #
@router.delete("/{chunk_id}", response_model=DeleteChunkResponse)
async def delete_chunk(
    chunk_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
):
    try:
        result = await chunk_service.delete(
            session=session,
            record_id=chunk_id,
        )

        return DeleteChunkResponse(success=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ---- Delete All Chunks By Subject + Book ---- #
@router.delete(
    "/subject/{subject_id}/book/{book_id}",
    response_model=DeleteChunkResponse,
)
async def delete_all_chunks_by_subject_and_book(
    subject_id: UUID,
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
):
    try:
        deleted_count = await chunk_service.delete_all_by_subject_and_book(
            session=session,
            subject_id=subject_id,
            book_id=book_id,
        )

        return DeleteChunkResponse(
            success=deleted_count > 0
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))