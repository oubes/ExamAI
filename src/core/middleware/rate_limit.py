# ---- Imports ---- #
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

# --- Logging ---- #
logger = logging.getLogger(__name__)

# ---- Redis Client ---- #
redis_client = Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

# ---- Limits ---- #
GLOBAL_RATE_LIMIT = (30, 60) 

RATE_LIMITS = {
    "/api/v1/identity/login": (2, 10),
    "/api/v1/identity/register": (2, 10),
    "/api/v1/identity/reset-password/request": (2, 10),
}


# ---- Middleware Registration ---- #
def register_rate_limit_middleware(app):

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):

        path = request.url.path

        # ---- config resolution ---- #
        limit, window = RATE_LIMITS.get(
            path,
            GLOBAL_RATE_LIMIT,
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