# ---- Imports ---- #
from fastapi import APIRouter

# ---- Router ---- #
router = APIRouter()

# ---- Routes ---- #
@router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "OK"
    }