# ---- Imports ---- #
from uuid import UUID
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.session import session_local
from src.auth.auth import get_current_user
from src.domain.identity.models.user import User
from src.services.knowledge.pipeline import knowledge_pipeline
from src.services.knowledge.service import knowledge_base_manager


# ---- Router ---- #
router = APIRouter()


# ---- DB Session ---- #
async def get_session():
    async with session_local() as session:
        yield session


# ---- Mapper ---- #
def map_chunk(chunk):
    return {
        "id": str(chunk.id),
        "subject_id": str(chunk.subject_id),
        "document_id": str(chunk.document_id),
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "summary": chunk.summary,
        "keywords": chunk.keywords,
        "source_type": chunk.source_type,
        "quality_score": chunk.quality_score,
        "importance_score": chunk.importance_score,
    }


# ---- Run Knowledge Pipeline ---- #
@router.post("/pipeline/run/{file_id}")
async def run_knowledge_pipeline(
    file_id: str,
    subject_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        result = await knowledge_pipeline.run(
            session=session,
            file_id=file_id,
            subject_id=subject_id,
        )

        return {
            "status": "success",
            "file_id": file_id,
            "subject_id": subject_id,
            "data": result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Get Chunk By ID ---- #
@router.get("/chunks/{chunk_id}")
async def get_chunk(
    chunk_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        chunk = await knowledge_base_manager.get_chunk(
            session=session,
            record_id=chunk_id,
        )

        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")

        return {
            "status": "success",
            "data": map_chunk(chunk),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- List Subject Chunks ---- #
@router.get("/chunks/subject/{subject_id}")
async def list_subject_chunks(
    subject_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        chunks = await knowledge_base_manager.list_subject_chunks(
            session=session,
            subject_id=subject_id,
            limit=limit,
            offset=offset,
        )

        return {
            "status": "success",
            "count": len(chunks),
            "data": [map_chunk(c) for c in chunks],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- List Document Chunks ---- #
@router.get("/chunks/document/{document_id}")
async def list_document_chunks(
    document_id: UUID,
    subject_id: UUID,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        chunks = await knowledge_base_manager.list_document_chunks(
            session=session,
            subject_id=subject_id,
            document_id=document_id,
            limit=limit,
        )

        return {
            "status": "success",
            "count": len(chunks),
            "data": [map_chunk(c) for c in chunks],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Search Chunks ---- #
@router.get("/chunks/search")
async def search_chunks(
    query: str,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        chunks = await knowledge_base_manager.search_chunks(
            session=session,
            query=query,
            limit=limit,
        )

        return {
            "status": "success",
            "count": len(chunks),
            "data": [map_chunk(c) for c in chunks],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Delete Chunk ---- #
@router.delete("/chunks/{chunk_id}")
async def delete_chunk(
    chunk_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        deleted = await knowledge_base_manager.delete_chunk(
            session=session,
            record_id=chunk_id,
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Chunk not found")

        return {
            "status": "success",
            "deleted": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Update Chunk (FINAL MATCHED) ---- #
@router.patch("/chunks/{chunk_id}")
async def update_chunk(
    chunk_id: UUID,
    payload: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        updated_count = await knowledge_base_manager.update_chunk(
            session=session,
            chunk_id=chunk_id,
            payload=payload,
        )

        return {
            "status": "success",
            "updated": updated_count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))