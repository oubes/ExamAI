# ---- Imports ---- #
from fastapi import APIRouter, Depends

from src.auth.auth import get_current_user
from src.auth.roles import admin_required, user_required


# ---- Router ---- #
router = APIRouter()


# ---- Routes ---- #
@router.get("/")
async def health_check():
    return {"status": "OK"}


# ---- Protected Example ---- #
@router.get("/secure-health")
async def secure_health(user=Depends(get_current_user), _=Depends(admin_required)):
    return {
        "status": "OK",
        "user": user
    }