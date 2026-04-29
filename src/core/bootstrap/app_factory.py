# ---- Imports ---- #
from fastapi import FastAPI
from core.bootstrap.lifespan import lifespan
from core.config.settings import get_settings

# ---- Settings ---- #
settings = get_settings()

# ---- App instance ---- #
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# ---- App Factory ---- #
def create_app():
    try:
        return app
    except Exception as e:
        print(e)