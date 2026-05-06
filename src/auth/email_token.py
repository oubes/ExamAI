# ---- Imports ---- #
from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt

from src.core.di.settings import get_settings


# ---- Settings ---- #
settings = get_settings()


# ---- Create Email Verification Token ---- #
def create_email_verification_token(user_id: UUID, email: str) -> str:

    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "email_verification",
        "iss": "examai",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.email_verification_token_expire_minutes),
    }

    return jwt.encode(payload, settings.email_secret_key, algorithm=settings.email_algorithm)


# ---- Decode + Verify Token ---- #
def decode_email_verification_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        settings.email_secret_key,
        algorithms=[settings.email_algorithm],
        options={"require": ["exp", "sub", "iat"]},
    )

    # ---- Extra safety check ---- #
    if payload.get("type") != "email_verification":
        raise ValueError("Invalid token type")

    return payload

# ---- Create Password Reset Token ---- #
def create_password_reset_token(user_id: str, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "password_reset",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    return jwt.encode(
        payload,
        settings.email_secret_key,
        algorithm=settings.email_algorithm,
    )

# ---- Decode Password Reset Token ---- #
def decode_password_reset_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.email_secret_key,
        algorithms=[settings.email_algorithm],
    )