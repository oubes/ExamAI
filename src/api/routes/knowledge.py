# ---- Imports ---- #
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.session import session_local
from src.auth.auth import get_current_user
from src.domain.identity.models.user import User

from src.services.knowledge.pipeline import knowledge_pipeline


# ---- Router ---- #
router = APIRouter()


# ---- DB Session ---- #
async def get_session():
    async with session_local() as session:
        yield session


# ---- Run Knowledge Pipeline ---- #
@router.post("/knowledge/pipeline/run/{file_id}")
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
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )