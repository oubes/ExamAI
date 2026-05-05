# ---- Imports ---- #
from uuid import UUID
from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.security import security
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models.identity_models import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RegisterResponse,
    MeResponse,
)
from src.auth.auth import (
    get_current_user,
    get_refresh_user,
)
from src.auth.jwt import decode_token
from src.infra.db.session import session_local
from src.domains.identity.models import User
from src.domains.identity.service import IdentityService
from src.infra.email.service import EmailService
from src.core.di.settings import get_settings

# ---- Settings ---- #
settings = get_settings()

# ---------- Router ---------- #
router = APIRouter()

identity_service = IdentityService()
email_service = EmailService()

# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session


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
        await email_service.send_from_template(
            to=user.email,
            template_name="welcome.yml",
            context={"username": user.user_name}
        )
        
        await email_service.send_from_template(
            to=user.email,
            template_name="verify_email.yml",
            context={
                "username": user.user_name,
                "verification_link": f"{settings.app_url}/api/v1/identity/verify/{user.id}/{user.email_verify_token}"
                # "verification_link": "https://www.google.com/"
            }
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
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


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

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


# ---------- Refresh ---------- #
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: User = Depends(get_refresh_user),
    session: AsyncSession = Depends(get_session),
):
    # ---- extract session id only ---- #
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        tokens = await identity_service.refresh_tokens(
            session=session,
            user=user,
            session_id=UUID(session_id),
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return TokenResponse(**tokens)


# ---------- Logout ---------- #
@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    # ---- decode token ---- #
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    # ---- service call ---- #
    try:
        await identity_service.logout(
            session=session,
            session_id=UUID(session_id),
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Logout failed")

    return {"message": "logged out"}


# ---------- Protected ---------- #
@router.get("/me", response_model=MeResponse)
async def me(
    user: User = Depends(get_current_user),
):
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