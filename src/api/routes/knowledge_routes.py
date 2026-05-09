# ---- Imports ---- #
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import get_current_user
from src.auth.roles import admin_required
from src.domains.identity.models import User
from src.infra.db.session import session_local
from src.services.knowledge.ingestion.chunker import KnowledgeIngestionChunker
from src.services.knowledge.ingestion.reader import KnowledgeChunkReader


# ---- Router ---- #
router = APIRouter()


# ---- Services ---- #
chunker = KnowledgeIngestionChunker()
reader = KnowledgeChunkReader()


# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session


# ---------- Request Models ---------- #
class IngestKnowledgeRequest(BaseModel):
    subject_id: int = Field(..., ge=1)
    pdf_path: str = Field(
        default="data/the-art-of-ancient-egypt-philippe-de-montebello-and-kent-lydecker.pdf"
    )


# ---- Ingest PDF ---- #
@router.post("/ingest")
async def ingest_pdf(
    payload: IngestKnowledgeRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(admin_required),
):
    source_path = Path(payload.pdf_path).expanduser().resolve()

    if not source_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found: {source_path}")

    rows = await chunker.ingest_pdf(
        session=session,
        pdf_path=source_path,
        subject_id=payload.subject_id,
    )

    return {
        "status": "completed",
        "requested_by": user.id,
        "source_file": source_path.as_posix(),
        "document_id": rows[0].document_id if rows else None,
        "ingested_chunks": len(rows),
    }


# ---- Read Chunks ---- #
@router.get("/documents/{document_id}/chunks")
async def list_document_chunks(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    rows = await reader.list_by_document(session=session, document_id=document_id)

    items = [
        reader.prepare_for_llm(record)
        for record in rows
    ]

    return {
        "document_id": document_id,
        "count": len(items),
        "chunks": items,
    }
