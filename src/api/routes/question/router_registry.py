# ---- Imports ---- #
from fastapi import APIRouter

from .content_segmentation import router as content_segmentation_router
from .chunks import router as chunks_router

# ---------- Main Router ---------- #
router = APIRouter()

router.include_router(content_segmentation_router, prefix="")
router.include_router(chunks_router, prefix="/chunks")