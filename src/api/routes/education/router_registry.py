# ---- Imports ---- #
from fastapi import APIRouter
from .subject import router as subject_router
from .chapter import router as chapter_router
from .topic import router as topic_router

# ---------- Main Router ---------- #
router = APIRouter()

# ---- Routes ---- #
router.include_router(subject_router, prefix="/subjects")
router.include_router(chapter_router, prefix="/chapters")
router.include_router(topic_router, prefix="/topics")