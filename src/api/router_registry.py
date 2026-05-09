# ---- Imports ---- #
from src.api.routes.health_routes import router as health_router
from src.api.routes.identity_routes import router as identity_router
from src.api.routes.upload import router as upload_router
from src.api.routes.knowledge_routes import router as knowledge_router
from src.api.routes.adaptive_exam_routes import router as adaptive_exam_router

# ---- Router registry ---- #
def register_routers(app):
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(identity_router, prefix="/api/v1/identity", tags=["Identity"])
    app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
    app.include_router(knowledge_router, prefix="/api/v1/knowledge", tags=["Knowledge"])
    app.include_router(adaptive_exam_router, prefix="/api/v1/adaptive-exam", tags=["Adaptive Exam"])