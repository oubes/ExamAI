# ---- Imports ---- #
from src.api.routes.health_routes import router as health_router
from src.api.routes.identity_routes import router as identity_router
from src.api.routes.upload import router as upload_router

# ---- Router registry ---- #
def register_routers(app):
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(identity_router, prefix="/api/v1/identity", tags=["Identity"])
    app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])