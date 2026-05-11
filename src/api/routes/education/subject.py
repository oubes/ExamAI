# ---- Imports ---- #
from uuid import UUID

from src.services.education.service import EducationService

from fastapi import APIRouter, Depends, HTTPException
from src.core.di.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.roles import admin_required

from src.api.models.education_models import (
    AddSubjectRequest,
    AddSubjectResponse,
    GetSubjectResponse,
    ListSubjectsResponse,
    UpdateSubjectRequest,
    UpdateSubjectResponse,
    DeleteSubjectResponse,
    HardDeleteSubjectResponse,
)

# ---- Router ---- #
router = APIRouter()

# ---- Service ---- #
education_service = EducationService()


# ---- Add Subject ---- #
@router.post(path="", response_model=AddSubjectResponse)
async def add_subject(
    payload: AddSubjectRequest,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> AddSubjectResponse:

    try:
        print("Adding subject with payload:", payload)
        subject = await education_service.add_subject(
            session=session,
            payload=payload.model_dump(),
        )

        return AddSubjectResponse(**subject)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )


# ---- Get Subject ---- #
@router.get(path="/{subject_id}", response_model=GetSubjectResponse)
async def get_subject(
    subject_id: UUID,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> GetSubjectResponse:

    try:
        subject = await education_service.get_subject(
            session=session,
            subject_id=subject_id,
        )

        return GetSubjectResponse(**subject)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )


# ---- List Subjects ---- #
@router.get(path="", response_model=ListSubjectsResponse)
async def list_subjects(
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> ListSubjectsResponse:

    try:
        subjects = await education_service.list_subjects(session=session)

        return ListSubjectsResponse(
            items=[
                GetSubjectResponse(**subject)
                for subject in subjects
            ]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---- List Deleted Subjects ---- #
@router.get(
    path="/deleted/list",
    response_model=ListSubjectsResponse,
)
async def list_deleted_subjects(
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> ListSubjectsResponse:

    try:
        subjects = await education_service.list_deleted_subjects(
            session=session,
        )

        return ListSubjectsResponse(
            items=[
                GetSubjectResponse(**subject)
                for subject in subjects
            ]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )

# ---- Update Subject ---- #
@router.put(path="/{subject_id}", response_model=UpdateSubjectResponse)
async def update_subject(
    subject_id: UUID,
    payload: UpdateSubjectRequest,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> UpdateSubjectResponse:

    try:
        subject = await education_service.update_subject(
            session=session,
            subject_id=subject_id,
            updates=payload.model_dump(exclude_none=True),
        )

        return UpdateSubjectResponse(**subject)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )


# ---- Delete ---- #
@router.delete(path="/{subject_id}", response_model=DeleteSubjectResponse)
async def delete_subject(
    subject_id: UUID,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> DeleteSubjectResponse:

    try:
        result = await education_service.delete_subject(
            session=session,
            subject_id=subject_id,
        )

        return DeleteSubjectResponse(
            success=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )
        
# ---- Hard Delete ---- #
@router.delete(
    path="/{subject_id}/hard",
    response_model=HardDeleteSubjectResponse,
)
async def hard_delete_subject(
    subject_id: UUID,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> HardDeleteSubjectResponse:

    try:
        result = await education_service.hard_delete_subject(
            session=session,
            subject_id=subject_id,
        )

        return HardDeleteSubjectResponse(
            success=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )
        
# ---- Restore Subject ---- #
@router.post(
    path="/{subject_id}/restore",
    response_model=GetSubjectResponse,
)
async def restore_subject(
    subject_id: UUID,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> GetSubjectResponse:

    try:
        subject = await education_service.restore_subject(
            session=session,
            subject_id=subject_id,
        )

        return GetSubjectResponse(**subject)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )
        
# ---- Toggle Active ---- #
@router.patch(
    path="/{subject_id}/toggle-active",
    response_model=GetSubjectResponse,
)
async def toggle_subject_active(
    subject_id: UUID,
    session: AsyncSession = Depends(dependency=get_session),
    _ = Depends(dependency=admin_required)
) -> GetSubjectResponse:

    try:
        subject = await education_service.toggle_subject_active(
            session=session,
            subject_id=subject_id,
        )

        return GetSubjectResponse(**subject)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(object=e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(object=e),
        )