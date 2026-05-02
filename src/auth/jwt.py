# ---- imports ---- #
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from src.core.di.settings import get_settings


# ---------- Logger ---------- #
logger = logging.getLogger(__name__)


# ---- settings ---- #
settings = get_settings()


# ---- create access token ---- #
def create_access_token(
    user_id: str,
    session_id: str,
) -> str:

    payload = {
        "sub": str(user_id),
        "type": "access",
        "session_id": str(session_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.access_token_expire_minutes),
        "jti": str(uuid4()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


# ---- create refresh token ---- #
def create_refresh_token(
    user_id: str,
    session_id: str,
) -> str:

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "session_id": str(session_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
        "jti": str(uuid4()),
    }

    return jwt.encode(
        payload,
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

    except jwt.PyJWTError as e:
        logger.exception(f"Token decoding failed: {e}")
        return None