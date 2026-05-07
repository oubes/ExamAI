# ---- Imports ---- #
from fastapi import APIRouter, UploadFile, Depends, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.roles import admin_required
from src.domains.identity.models import User
from src.infra.db.session import session_local
from src.infra.storage.service import StorageService
from src.auth.auth import get_current_user
from src.services.upload.service import UploadService


# ---- Router ---- #
router = APIRouter()


# ---- Dependencies ---- #
storage_service = StorageService()
upload_service = UploadService()

# ---------- DB Session ---------- #
async def get_session():
    async with session_local() as session:
        yield session


# ---- Upload Endpoint ---- #
@router.post("/{category}")
async def upload_file(
    category: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    _= Depends(admin_required)
):

    return await upload_service.handle_upload(session=session, user=user, category=category, file=file)