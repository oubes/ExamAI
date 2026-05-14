# ---- Imports ---- #
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import get_current_user

from src.domain.identity.models.user import User

from src.infra.db.session import session_local

from src.services.profile.service import ProfileService

from src.api.models.profile_models import (
    ProfileResponse,
    ProfileUpdateRequest,
    ProfileStatsResponse,
    PublicProfileResponse,
)


# ---- Router ---- #
router = APIRouter()


# ---- Services ---- #
profile_service = ProfileService()


# ---- DB Session ---- #
async def get_session():

    async with session_local() as session:
        yield session


# ---- Get My Profile ---- #
@router.get(
    "/me",
    response_model=ProfileResponse,
)
async def get_my_profile(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    record = await profile_service.get_profile(
        session=session,
        user_id=user.id,
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="profile not found",
        )

    return record


# ---- Update My Profile ---- #
@router.put(
    "/me",
    response_model=ProfileResponse,
)
async def update_my_profile(
    payload: ProfileUpdateRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    updated = await profile_service.update_profile(
        session=session,
        user_id=user.id,
        updates=payload.model_dump(
            exclude_unset=True,
        ),
    )

    return updated


# ---- Public Profile ---- #
@router.get(
    "/public/{user_name}",
    response_model=PublicProfileResponse,
)
async def get_public_profile(
    user_name: str,
    session: AsyncSession = Depends(get_session),
):

    record = await profile_service.get_public_profile(
        session=session,
        user_name=user_name,
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="profile not found",
        )

    return PublicProfileResponse(
        **record,
    )


# ---- Profile Stats ---- #
@router.get(
    "/stats/me",
    response_model=ProfileStatsResponse,
)
async def get_profile_stats(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    stats = await profile_service.get_profile_stats(
        session=session,
        user_id=user.id,
    )

    return ProfileStatsResponse(
        **stats,
    )