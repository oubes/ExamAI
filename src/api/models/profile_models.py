# ---- Imports ---- #
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# ---- Base Profile ---- #
class ProfileBase(BaseModel):

    full_name: str
    user_name: str
    email: EmailStr


# ---- Profile Response ---- #
class ProfileResponse(ProfileBase):

    id: UUID

    role: str

    is_active: bool
    is_verified: bool

    global_learning_velocity: float
    preferred_difficulty_band: float

    model_config = ConfigDict(
        from_attributes=True,
    )


# ---- Profile Update Request ---- #
class ProfileUpdateRequest(BaseModel):

    full_name: str | None = None
    user_name: str | None = None
    email: EmailStr | None = None

    password_hash: str | None = None

    preferred_difficulty_band: float | None = None


# ---- Public Profile Response ---- #
class PublicProfileResponse(BaseModel):

    id: UUID

    full_name: str
    user_name: str

    global_learning_velocity: float
    preferred_difficulty_band: float

    is_verified: bool


# ---- Profile Stats Response ---- #
class ProfileStatsResponse(BaseModel):

    attempts: int
    enrollments: int