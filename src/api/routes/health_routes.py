# ---- Imports ---- #
from fastapi import APIRouter, Depends

from src.auth.deps import get_current_user


# ---- Router ---- #
router = APIRouter()


# ---- Routes ---- #
@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "OK"}


# ---- Protected Example ---- #
@router.get("/secure-health")
async def secure_health(user=Depends(get_current_user)):
    return {
        "status": "OK",
        "user": user
    }