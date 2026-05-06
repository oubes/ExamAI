# ---- Imports ---- #
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from src.core.di.settings import get_settings

# ---- Settings ---- #
settings = get_settings()

# --- Logging ---- #
logger = logging.getLogger(__name__)

# ---- Redis Client ---- #
redis_client = Redis(
    host=settings.rate_limit_host,
    port=settings.rate_limit_port,
    decode_responses=True,
)


# ---- Middleware Registration ---- #
def register_rate_limit_middleware(app):

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):

        path = request.url.path

        # ---- config resolution ---- #
        limit, window = settings.rate_limits.get(
            path,
            settings.global_rate_limit,
        )

        ip = request.client.host if request.client else "unknown"

        key = f"rate_limit:{path}:{ip}"

        current = await redis_client.incr(key)

        if current == 1:
            await redis_client.expire(key, window)

        if current > limit:
            logger.warning(
                f"Rate limit hit: {request.method} {path} ip={ip} count={current}"
            )

            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(window)},
            )

        return await call_next(request)