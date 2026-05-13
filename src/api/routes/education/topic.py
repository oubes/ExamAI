# ---- Imports ---- #
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.db import get_session
from src.auth.roles import admin_required

from src.services.education.topic_service import TopicService

from src.api.models.education_models.topic_models import (
    AddTopicRequest,
    AddTopicResponse,
    GetTopicResponse,
    ListTopicsResponse,
    UpdateTopicRequest,
    UpdateTopicResponse,
    DeleteTopicResponse,
)

# ---- Router ---- #
router = APIRouter()

# ---- Service ---- #
topic_service = TopicService()


# ---- Add Topic ---- #
@router.post(path="", response_model=AddTopicResponse)
async def add_topic(
    payload: AddTopicRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> AddTopicResponse:
    try:
        topic = await topic_service.add_topic(
            session=session,
            payload=payload.model_dump(),
        )

        return AddTopicResponse(**topic)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Get Topic ---- #
@router.get(path="/{topic_id}", response_model=GetTopicResponse)
async def get_topic(
    topic_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> GetTopicResponse:
    try:
        topic = await topic_service.get_topic(
            session=session,
            topic_id=topic_id,
        )

        return GetTopicResponse(**topic)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- List Topics ---- #
@router.get(path="", response_model=ListTopicsResponse)
async def list_topics(
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> ListTopicsResponse:
    try:
        topics = await topic_service.list_topics(session=session)

        return ListTopicsResponse(
            items=[GetTopicResponse(**t) for t in topics]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Update Topic ---- #
@router.put(path="/{topic_id}", response_model=UpdateTopicResponse)
async def update_topic(
    topic_id: UUID,
    payload: UpdateTopicRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> UpdateTopicResponse:
    try:
        topic = await topic_service.update_topic(
            session=session,
            topic_id=topic_id,
            updates=payload.model_dump(exclude_none=True),
        )

        return UpdateTopicResponse(**topic)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Delete Topic ---- #
@router.delete(path="/{topic_id}", response_model=DeleteTopicResponse)
async def delete_topic(
    topic_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> DeleteTopicResponse:
    try:
        result = await topic_service.delete_topic(
            session=session,
            topic_id=topic_id,
        )

        return DeleteTopicResponse(success=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
