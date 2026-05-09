# ---- Imports ---- #
from fastapi import APIRouter

from .register import router as register_router
from .login import router as login_router
from .verify_email import router as verify_router
from .reset_password import router as reset_router
from .refresh import router as refresh_router
from .logout import router as logout_router
from .me import router as me_router

# ---------- Main Router ---------- #
router = APIRouter()

router.include_router(register_router, prefix="")
router.include_router(login_router, prefix="")
router.include_router(verify_router, prefix="")
router.include_router(reset_router, prefix="")
router.include_router(refresh_router, prefix="")
router.include_router(logout_router, prefix="")
router.include_router(me_router, prefix="")