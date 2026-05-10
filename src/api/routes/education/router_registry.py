# ---- Imports ---- #
from fastapi import APIRouter
from .subject import router as subject_router

# ---------- Main Router ---------- #
router = APIRouter()

# ---- Routes ---- #
router.include_router(subject_router, prefix="/subjects")