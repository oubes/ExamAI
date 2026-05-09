# ---- Imports ---- #
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models.identity_models import LoginRequest, TokenResponse
from src.auth.service import IdentityService
from .deps import get_session

# ---------- Router ---------- #
router = APIRouter()

identity_service = IdentityService()

# ---------- Login ---------- #
@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        tokens = await identity_service.login(
            session=session,
            payload={
                "email": payload.email,
                "password": payload.password,
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        return TokenResponse(**tokens)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))