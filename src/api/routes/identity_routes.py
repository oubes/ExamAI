# ---- Imports ---- #
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models.auth_models import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from src.auth.deps import (
    get_current_user,
    get_refresh_user,
)
from src.db.session import session_local
from src.domains.identity.models import User
from src.domains.identity.service import UserService


# ---------- Router ---------- #
router = APIRouter()

auth_service = UserService()


# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session


# ---------- Register Endpoint ---------- #
@router.post("/register")
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await auth_service.register(
            session=session,
            full_name=payload.full_name,
            email=payload.email,
            password=payload.password,
        )

        return {
            "id": user.id,
            "email": user.email,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ---------- Login Endpoint ---------- #
@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        tokens = await auth_service.login(
            session=session,
            email=payload.email,
            password=payload.password,
        )

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


# ---------- Refresh Endpoint ---------- #
@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    user: User = Depends(get_refresh_user),
):
    tokens = auth_service.generate_tokens(user)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )


# ---------- Protected Endpoint ---------- #
@router.get("/me")
async def me(
    user: User = Depends(get_current_user),
):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    }