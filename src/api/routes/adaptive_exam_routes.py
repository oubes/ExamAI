# ---- Imports ---- #
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import get_current_user
from src.auth.roles import admin_required
from src.domain.adaptive_exam.models.generated_exam_session import GeneratedExamSession
from src.domains.identity.models import User
from src.infra.db.session import session_local
from src.services.knowledge.ingestion.pipeline import AdaptiveExamQuestionPipeline


# ---- Router ---- #
router = APIRouter()


# ---- Services ---- #
pipeline = AdaptiveExamQuestionPipeline()


# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session


# ---------- Request Models ---------- #
class GenerateAdaptiveQuestionsRequest(BaseModel):
    document_id: int = Field(..., ge=1)
    exam_id: int | None = Field(default=None, ge=1)
    exam_title: str | None = None
    questions_per_chunk: int = Field(default=4, ge=1, le=8)


# ---- Generate Adaptive Questions ---- #
@router.post("/sessions/{session_id}/generate")
async def generate_adaptive_questions(
    session_id: int,
    payload: GenerateAdaptiveQuestionsRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    _=Depends(admin_required),
):
    generated_session = await session.get(GeneratedExamSession, session_id)

    if generated_session is None:
        raise HTTPException(status_code=404, detail=f"Generated exam session not found: {session_id}")

    created = await pipeline.generate_for_document(
        session=session,
        generated_exam_session=generated_session,
        document_id=payload.document_id,
        exam_id=payload.exam_id,
        exam_title=payload.exam_title,
        questions_per_chunk=payload.questions_per_chunk,
    )

    return {
        "status": "completed",
        "requested_by": user.id,
        "session_id": session_id,
        "document_id": payload.document_id,
        "created_generated_exam_questions": len(created),
    }
