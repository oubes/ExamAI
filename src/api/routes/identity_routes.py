# ---- Imports ---- #
import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import update
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
from src.auth.jwt import decode_token
from src.db.session import session_local
from src.domains.identity.models import (
    User,
    UserSession,
)
from src.domains.identity.service import UserService


# ---------- Router ---------- #
router = APIRouter()

auth_service = UserService()
security = HTTPBearer()


# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session


# ---------- Register ---------- #
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


# ---------- Login ---------- #
@router.post("/login", response_model=TokenResponse)
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
):
    # ---- decode token ---- #
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    # ---- extract session id ---- #
    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        )

    # ---- rotate tokens using same session ---- #
    tokens = auth_service.generate_tokens(
        user=user,
        session_id=session_id,
    )

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
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    # ---- extract session id ---- #
    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        )

    # ---- deactivate session ---- #
    await session.execute(
        update(UserSession)
        .where(UserSession.id == UUID(session_id))
        .values(is_active=False)
    )

    await session.commit()

    return {"message": "logged out"}


# ---------- Protected ---------- #
@router.get("/me")
async def me(
    user: User = Depends(get_current_user),
):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    }