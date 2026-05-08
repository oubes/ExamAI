# ---- Imports ---- #
from uuid import UUID
from datetime import datetime
from typing import cast

from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.email_token import create_email_verification_token, decode_email_verification_token
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
from src.infra.queue.email_tasks import (
    send_welcome_email,
    send_verify_email,
    send_reset_password_email,
)

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

        token = create_email_verification_token(
            user_id=user.id,
            email=user.email,
        )

        verification_link = (
            f"{settings.app_url}/api/v1/identity/verify?token={token}"
        )

        send_welcome_email.delay(
            user.email,
            {"username": user.user_name},
        )

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
        
# ---------- Verify Email ---------- #
@router.get("/verify")
async def verify_email(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    payload = decode_email_verification_token(token)

    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    await identity_service.verify_email(
        session=session,
        user_id=user_id,
        email=email,
    )

    return {"message": "Email verified successfully"}

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

# ---------- Request Password Reset ---------- #
@router.post("/reset-password/request")
async def request_reset(
    email: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        to, link = await identity_service.create_password_reset(
            session=session,
            email=email,
        )

        send_reset_password_email.delay(
            to,
            {
                "username": email,
                "reset_link": link,
            },
        )

        return {"message": "reset email sent"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/reset-password/confirm")
def reset_password_page(token: str):

    return HTMLResponse(f"""
        <form action="/api/v1/identity/reset-password/confirm" method="post">
            <input name="token" value="{token}" hidden />
            <input name="new_password" type="password" />
            <button type="submit">Reset</button>
        </form>
    """)

# ---------- Confirm Password Reset ---------- #
@router.post("/reset-password/confirm")
async def reset_password_confirm(
    token: str = Form(...),
    new_password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    try:
        await identity_service.reset_password(
            session=session,
            token=token,
            new_password=new_password,
        )

        return {"message": "password reset successful"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------- Refresh ---------- #
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: User = Depends(get_refresh_user),
    session: AsyncSession = Depends(get_session),
):
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
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid session")

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