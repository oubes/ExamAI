# ---- Imports ---- #
from src.api.routes.health_routes import router as health_router
from src.api.routes.auth_routes import router as auth_router

# ---- Router registry ---- #
def register_routers(app):
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])