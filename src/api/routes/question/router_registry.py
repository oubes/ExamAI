# ---- Imports ---- #
from fastapi import APIRouter

from .content_segmentation import router as content_segmentation_router
from .chunks import router as chunks_router
from .question_generation import router as question_generation_router

# ---------- Main Router ---------- #
router = APIRouter()

router.include_router(content_segmentation_router, prefix="")
router.include_router(chunks_router, prefix="/chunks")
router.include_router(question_generation_router, prefix="/question_generation")