# ---- imports ---- #
from passlib.context import CryptContext
from src.core.di.settings import get_settings


# ---- settings ---- #
settings = get_settings()

pwd_context = CryptContext(
    schemes=[settings.password_hash_algorithm],
    deprecated="auto",
)


# ---- hash password ---- #
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ---- verify password ---- #
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)