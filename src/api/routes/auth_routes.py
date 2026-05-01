# ---- Imports ---- #
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from src.db.session import session_local
from src.auth.deps import get_current_user
from src.auth.service import AuthService


# ---------- Router ---------- #
router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


# ---- DB Session ---- #
async def get_session():
    async with session_local() as session:
        yield session


# ---- Register Endpoint ---- #
@router.post("/register")
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await auth_service.register(
            session,
            payload.full_name,
            payload.email,
            payload.password,
        )

        return {"id": user.id, "email": user.email}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- Login Endpoint ---- #
@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        token = await auth_service.login(
            session,
            payload.email,
            payload.password,
        )

        return TokenResponse(access_token=token)

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# ---- Protected Test Endpoint ---- #
@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user