# ---- Imports ---- #
from src.api.routes.health_routes import router as health_router
# from src.api.routes.identity_routes import router as identity_router
from src.api.routes.upload import router as upload_router
from src.api.routes.identity_routes.router_registry import router as identity_router
from src.api.routes.education.router_registry import router as education_router
from src.api.routes.question.router_registry import router as question_router

# ---- Router registry ---- #
def register_routers(app):
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(identity_router, prefix="/api/v1/identity", tags=["Identity"])
    app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
    app.include_router(education_router, prefix="/api/v1/education", tags=["Education"])
    app.include_router(question_router, prefix="/api/v1/question", tags=["Question"])