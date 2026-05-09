# ---- Imports ---- #
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.email_token import decode_email_verification_token
from src.auth.service import IdentityService
from src.core.di.settings import get_settings

from .deps import get_session

# ---- Settings ---- #
settings = get_settings()

# ---------- Router ---------- #
router = APIRouter()

identity_service = IdentityService()

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

    return RedirectResponse(
        url=f"{settings.frontend_url}/AuthPage?verified=1",
        status_code=302
    )