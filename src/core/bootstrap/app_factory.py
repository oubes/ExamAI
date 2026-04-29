# ---- Imports ---- #
from fastapi import FastAPI
import logging
from src.core.bootstrap.lifespan import lifespan
from src.core.di.settings import get_settings
from src.api.router_registry import register_routers
from src.core.middleware import register_middleware

# ---- Settings ---- #
settings = get_settings()

# ---- Logging ---- #
logging = logging.getLogger(__name__)

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
        register_middleware(app)
        logging.info("App created successfully")
        return app
        
    except Exception as e:
        logging.error(f"Error creating app: {e}")