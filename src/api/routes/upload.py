# ---- Imports ---- #
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import get_current_user
from src.auth.roles import admin_required

from src.domain.identity.models.user import User

from src.infra.db.session import session_local

from src.services.upload.service import UploadService

from src.api.models.upload_models import (
    UploadResponse,
    DeleteUploadResponse,
    UploadStatsResponse,
    UploadListQuery,
)


# ---- Router ---- #
router = APIRouter()


# ---- Services ---- #
upload_service = UploadService()


# ---- DB Session ---- #
async def get_session():

    async with session_local() as session:
        yield session


# ---- Upload Endpoint ---- #
@router.post(
    "/{category}",
    response_model=UploadResponse,
)
async def upload_file(
    category: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    # _=Depends(admin_required),
):

    return await upload_service.handle_upload(
        session=session,
        user=user,
        category=category,
        file=file,
    )


# ---- Get Upload ---- #
@router.get(
    "/{file_id}",
    response_model=UploadResponse,
)
async def get_upload(
    file_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    record = await upload_service.get_upload(
        session=session,
        file_id=file_id,
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="upload not found",
        )

    if record.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="forbidden",
        )

    return record


# ---- Get User Uploads ---- #
@router.get(
    "/",
    response_model=list[UploadResponse],
)
async def get_user_uploads(
    query: UploadListQuery = Depends(),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    return await upload_service.get_user_uploads(
        session=session,
        user_id=user.id,
        category=query.category,
        limit=query.limit,
        offset=query.offset,
    )


# ---- Delete Upload ---- #
@router.delete(
    "/{file_id}",
    response_model=DeleteUploadResponse,
)
async def delete_upload(
    file_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    record = await upload_service.get_upload(
        session=session,
        file_id=file_id,
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="upload not found",
        )

    if record.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="forbidden",
        )

    deleted = await upload_service.delete_upload(
        session=session,
        file_id=file_id,
    )

    return DeleteUploadResponse(
        deleted=deleted,
    )


# ---- Upload Stats ---- #
@router.get(
    "/stats/me",
    response_model=UploadStatsResponse,
)
async def upload_stats(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    stats = await upload_service.stats(
        session=session,
        user_id=user.id,
    )

    return UploadStatsResponse(
        **stats,
    )