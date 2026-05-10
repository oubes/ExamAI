# ---- Imports ---- #
from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends

from src.api.models.identity_models import MeResponse
from src.auth.auth import get_current_user
from src.domain.identity.models.user import User

router = APIRouter()

# ---------- Me ---------- #
@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)):
    return MeResponse(
        id=user.id,
        full_name=user.full_name,
        user_name=user.user_name,
        role=user.role,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=cast(datetime, user.created_at),
        updated_at=cast(datetime, user.updated_at),
    )