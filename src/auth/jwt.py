# ---- imports ---- #
import jwt
from datetime import datetime, timedelta, timezone

from src.core.di.settings import get_settings


# ---- settings ---- #
settings = get_settings()


# ---- create token ---- #
def create_token(payload: dict) -> str:
    data = payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    data.update({"exp": expire})

    return jwt.encode(
        data,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


# ---- decode token ---- #
def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except Exception:
        return None