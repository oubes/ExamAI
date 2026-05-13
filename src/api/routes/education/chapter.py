# ---- Imports ---- #
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.db import get_session
from src.auth.roles import admin_required

from src.services.education.chapter_service import ChapterService

from src.api.models.education_models.chapter_models import (
    AddChapterRequest,
    AddChapterResponse,
    GetChapterResponse,
    ListChaptersResponse,
    UpdateChapterRequest,
    UpdateChapterResponse,
    DeleteChapterResponse,
)

# ---- Router ---- #
router = APIRouter()

# ---- Service ---- #
chapter_service = ChapterService()


# ---- Add Chapter ---- #
@router.post(path="", response_model=AddChapterResponse)
async def add_chapter(
    payload: AddChapterRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> AddChapterResponse:
    try:
        chapter = await chapter_service.add_chapter(
            session=session,
            payload=payload.model_dump(),
        )

        return AddChapterResponse(**chapter)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Get Chapter ---- #
@router.get(path="/{chapter_id}", response_model=GetChapterResponse)
async def get_chapter(
    chapter_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> GetChapterResponse:
    try:
        chapter = await chapter_service.get_chapter(
            session=session,
            chapter_id=chapter_id,
        )

        return GetChapterResponse(**chapter)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- List Chapters ---- #
@router.get(path="", response_model=ListChaptersResponse)
async def list_chapters(
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> ListChaptersResponse:
    try:
        chapters = await chapter_service.list_chapters(session=session)

        return ListChaptersResponse(
            items=[GetChapterResponse(**c) for c in chapters]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Update Chapter ---- #
@router.put(path="/{chapter_id}", response_model=UpdateChapterResponse)
async def update_chapter(
    chapter_id: UUID,
    payload: UpdateChapterRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> UpdateChapterResponse:
    try:
        chapter = await chapter_service.update_chapter(
            session=session,
            chapter_id=chapter_id,
            updates=payload.model_dump(exclude_none=True),
        )

        return UpdateChapterResponse(**chapter)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Delete Chapter ---- #
@router.delete(path="/{chapter_id}", response_model=DeleteChapterResponse)
async def delete_chapter(
    chapter_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_required),
) -> DeleteChapterResponse:
    try:
        result = await chapter_service.delete_chapter(
            session=session,
            chapter_id=chapter_id,
        )

        return DeleteChapterResponse(success=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
