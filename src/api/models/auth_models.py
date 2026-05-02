# ---- Imports ---- #
from pydantic import BaseModel, EmailStr


# ---------- Schemas ---------- #

# ---- Register Request ---- #
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# ---- Login Request ---- #
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---- Token Response ---- #
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"