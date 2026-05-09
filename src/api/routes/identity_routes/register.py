# ---- Imports ---- #
from datetime import datetime
from typing import cast

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models.identity_models import RegisterRequest, RegisterResponse
from src.auth.service import IdentityService
from src.core.di.settings import get_settings
from src.infra.queue.tasks import send_welcome_email, send_verify_email
from src.auth.email_token import create_email_verification_token

from .deps import get_session

# ---- Settings ---- #
settings = get_settings()

# ---------- Router ---------- #
router = APIRouter()

identity_service = IdentityService()

# ---------- Register ---------- #
@router.post("/register", response_model=RegisterResponse)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await identity_service.register(
            session=session,
            payload={
                "full_name": payload.full_name,
                "email": payload.email,
                "password": payload.password,
                "user_name": payload.user_name,
            }
        )

        token = create_email_verification_token(
            user_id=user.id,
            email=user.email,
        )

        verification_link = f"{settings.app_url}/api/v1/identity/verify?token={token}"

        send_welcome_email.delay(user.email, {"username": user.user_name})

        send_verify_email.delay(
            user.email,
            {
                "username": user.user_name,
                "verification_link": verification_link,
            },
        )

        return RegisterResponse(
            id=user.id,
            full_name=user.full_name,
            user_name=user.user_name,
            role=user.role,
            email=user.email,
            is_active=user.is_active,
            created_at=cast(datetime, user.created_at),
            updated_at=cast(datetime, user.updated_at),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))