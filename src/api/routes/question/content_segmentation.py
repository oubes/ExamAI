# ----- IMPORTS ----- #
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.db import get_session
from src.infra.queue.tasks import segment_file
from src.auth.roles import admin_required

from src.services.question.pipeline.segmentation_pipeline import run_pipeline as run_segmentation_pipeline
from src.infra.queue.tasks import run_question_pipeline


# ----- ROUTER ----- #
router = APIRouter()

# ----- RUN PIPELINE ----- #
@router.post(path="/run_segmentation_pipeline/{subject_id}")
async def run_pipeline(
    subject_id: UUID,
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
    # _=Depends(admin_required),
):
    try:

        result = await run_segmentation_pipeline(
            session=session,
            subject_id=subject_id,
            book_id=book_id,
        )
        
        # result = run_question_pipeline.delay(
        #     subject_id=str(subject_id),
        #     book_id=str(book_id),
        # )


        return {
            "success": True,
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )