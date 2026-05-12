# ---- Imports ---- #
from fastapi import APIRouter

from .content_segmentation import router as content_segmentation_router

# ---------- Main Router ---------- #
router = APIRouter()

router.include_router(content_segmentation_router, prefix="")