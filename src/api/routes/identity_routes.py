# ---- Imports ---- #
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import update, select
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
from src.domains.identity.service import IdentityService


# ---------- Router ---------- #
router = APIRouter()

identity_service = IdentityService()
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
        user = await identity_service.register(
            session=session,
            payload={
                "full_name": payload.full_name,
                "email": payload.email,
                "password": payload.password,
                "user_name": payload.user_name,
            }
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
    # ---- decode token ---- #
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        )

    # ---- validate session ---- #
    result = await session.execute(
        select(UserSession).where(
            UserSession.id == UUID(session_id),
        )
    )

    db_session = result.scalar_one_or_none()

    if not db_session:
        raise HTTPException(
            status_code=401,
            detail="Session not found",
        )

    if not db_session.is_active:
        raise HTTPException(
            status_code=401,
            detail="Session revoked",
        )

    if db_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Session expired",
        )

    # ---- rotate tokens ---- #
    tokens = identity_service.generate_tokens(
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