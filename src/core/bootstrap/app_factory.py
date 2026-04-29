# ---- Imports ---- #
from fastapi import FastAPI
from core.bootstrap.lifespan import lifespan
from core.config.settings import get_settings
from api.router_registry import register_routers

# ---- Settings ---- #
settings = get_settings()

# ---- App Factory ---- #
def create_app():
    try:
        app = FastAPI(
            title=settings.app_name,
            description=settings.app_description,
            version=settings.app_version,
            lifespan=lifespan,
        )
        register_routers(app)
        return app
        
    except Exception as e:
        print(e)