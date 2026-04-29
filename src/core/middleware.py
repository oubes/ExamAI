# ---- Imports ---- #
import time
import logging
from fastapi import Request

# --- Logging ---- #
logging = logging.getLogger(__name__)

# --- Middleware Registration ---- #
def register_middleware(app):
    @app.middleware("http")
    async def log_time(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        end = time.perf_counter()
        duration = end - start
        
        if duration > 1.0:
            logging.warning(
                f"Slow request: {request.method} {request.url.path} took {duration:.2f} seconds"
            )
        elif  duration < 0.001:
            logging.info(
                f"Super fast request: {request.method} {request.url.path} took {duration*1000000:.2f} us"
            )
        else:
            logging.info(
                f"Fast request: {request.method} {request.url.path} took {duration*1000:.2f} ms"
            )
        
        return response