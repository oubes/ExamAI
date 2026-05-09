# ---- Imports ---- #
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from src.api.models.identity_models import ResetPasswordRequest
from src.auth.service import IdentityService
from src.infra.queue.tasks import send_reset_password_email, send_password_changed_email
from src.core.di.settings import get_settings

from .deps import get_session

# ---- Settings ---- #
settings = get_settings()

router = APIRouter()
identity_service = IdentityService()

# ---------- Request Reset ---------- #
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

        send_reset_password_email.delay(to, {"username": email, "reset_link": link})
        return {"message": "reset email sent"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Redirect Page ---------- #
@router.get("/reset-password/confirm")
def reset_password_page(token: str):
    return RedirectResponse(
        url=f"{settings.frontend_url}/reset_password?token={token}",
        status_code=302
    )


# ---------- Confirm Reset ---------- #
@router.post("/reset-password/confirm")
async def reset_password_confirm(
    payload: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await identity_service.reset_password(
            session=session,
            token=payload.token,
            new_password=payload.new_password,
        )

        send_password_changed_email.delay(
            user.email,
            {"username": user.user_name},
        )

        return {"message": "Password updated successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))