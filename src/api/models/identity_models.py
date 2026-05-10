# ---- Imports ---- #
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


# -------------------- models -------------------- #

# ---------- Registration ---------- #

# ---- Register Request ---- #
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    user_name: str

# ---- Register Response ---- #
class RegisterResponse(BaseModel):
    id: UUID
    full_name: str
    user_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- Login Request ---- #
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---- Token Response ---- #
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
# ---- Me Response ---- #
class MeResponse(BaseModel):
    id: UUID
    full_name: str
    user_name: str
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str