# ----- IMPORTS ----- #
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.db import get_session
from src.services.question.pipeline.question_pipeline import run_question_pipeline
from src.services.question.question_service import QuestionAggregateService

from src.api.models.question_models import (
    QuestionBundleResponse,
    QuestionBundleListResponse,
    QuestionBundleUpdateRequest,
    DeleteQuestionResponse,
    QuestionListQuery,
)

# ----- ROUTER ----- #
router = APIRouter()

# ----- SERVICES ----- #
question_aggregate_service = QuestionAggregateService()


# ----- RUN PIPELINE ----- #
@router.post("/run_question_pipeline/{subject_id}")
async def run_pipeline(
    subject_id: UUID,
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await run_question_pipeline(
            session=session,
            subject_id=str(subject_id),
            book_id=str(book_id),
        )

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- GET QUESTION ----- #
@router.get("/{question_id}")
async def get_question(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    try:
        record = await question_aggregate_service.get_full_question(
            session=session,
            question_id=question_id,
        )

        if not record:
            raise HTTPException(status_code=404, detail="question not found")

        return record

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- LIST QUESTIONS ----- #
@router.get("/")
async def list_questions(
    query: QuestionListQuery = Depends(),
    session: AsyncSession = Depends(get_session),
):
    try:
        records = await question_aggregate_service.list_full_questions(
            session=session,
            subject_id=query.subject_id,
            chapter_id=query.chapter_id,
            topic_id=query.topic_id,
            limit=query.limit,
            offset=query.offset,
        )

        return records

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- SEARCH QUESTIONS ----- #
@router.get("/search/text")
async def search_questions(
    q: str,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    try:
        records = await question_aggregate_service.search_questions(
            session=session,
            query=q,
            limit=limit,
        )

        return records

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- UPDATE QUESTION ----- #
@router.put("/{question_id}")
async def update_question(
    question_id: UUID,
    payload: QuestionBundleUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        existing = await question_aggregate_service.get_full_question(
            session=session,
            question_id=question_id,
        )

        if not existing:
            raise HTTPException(status_code=404, detail="question not found")

        updated = await question_aggregate_service.update_full_question(
            session=session,
            question_id=question_id,
            payload=payload.model_dump(exclude_unset=True),
        )

        return updated

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- DELETE QUESTION ----- #
@router.delete("/{question_id}", response_model=DeleteQuestionResponse)
async def delete_question(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    try:
        existing = await question_aggregate_service.get_full_question(
            session=session,
            question_id=question_id,
        )

        if not existing:
            raise HTTPException(status_code=404, detail="question not found")

        deleted = await question_aggregate_service.delete_full_question(
            session=session,
            question_id=question_id,
        )

        return DeleteQuestionResponse(deleted=deleted)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))