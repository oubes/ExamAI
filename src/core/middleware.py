# ---- Imports ---- #
import time
import logging
from fastapi import Request

# --- Logging ---- #
logging = logging.getLogger(__name__)

def register_middleware(app):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        end = time.time()
        
        duration = end - start
        if duration > 1.0:
            logging.warning(
                f"Slow request: {request.method} {request.url.path} took {duration:.2f} seconds"
            )
        else:
            logging.info(
                f"{request.method}, {request.url.path}, Duration: {duration*1000:.2f} ms"
            )
        
        return response