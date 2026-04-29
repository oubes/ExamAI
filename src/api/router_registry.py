# ---- Imports ---- #
from src.api.routes.health_routes import router as health_router

# ---- Router registry ---- #
def register_routers(app):
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])