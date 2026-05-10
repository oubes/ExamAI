# ---- Imports ---- #
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends

from src.auth.jwt import decode_token
from src.auth.security import security
from src.auth.service import IdentityService

from src.core.di.db import get_session

router = APIRouter()
identity_service = IdentityService()

# ---------- Logout ---------- #
@router.post("/logout")
async def logout(
    credentials=Depends(security),
    session=Depends(get_session),
):
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401)

    session_id = payload.get("session_id")

    await identity_service.logout(
        session=session,
        session_id=UUID(session_id),
    )

    return {"message": "logged out"}