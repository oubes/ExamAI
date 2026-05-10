# ---- Imports ---- #
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models.identity_models import TokenResponse
from src.auth.jwt import decode_token
from src.auth.auth import get_refresh_user
from src.auth.security import security
from src.domain.identity.models.user import User
from src.auth.service import IdentityService

from src.core.di.db import get_session

router = APIRouter()
identity_service = IdentityService()

# ---------- Refresh ---------- #
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    credentials=Depends(security),
    user: User = Depends(get_refresh_user),
    session: AsyncSession = Depends(get_session),
):
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401)

    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401)

    tokens = await identity_service.refresh_tokens(
        session=session,
        user=user,
        session_id=UUID(session_id),
    )

    return TokenResponse(**tokens)