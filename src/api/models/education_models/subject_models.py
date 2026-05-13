# ---- Imports ---- #
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# -------------------- models -------------------- #

# ---------- Subject ---------- #

# ---- Request ---- #
class AddSubjectRequest(BaseModel):
    title: str
    code: str
    description: str
    is_active: bool


# ---- Response ---- #
class AddSubjectResponse(BaseModel):
    id: UUID
    title: str
    code: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- Get ---- #
class GetSubjectResponse(BaseModel):
    id: UUID
    title: str
    code: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- List ---- #
class ListSubjectsResponse(BaseModel):
    items: list[GetSubjectResponse]


# ---- Update Request ---- #
class UpdateSubjectRequest(BaseModel):
    title: str | None = None
    code: str | None = None
    description: str | None = None
    is_active: bool | None = None


# ---- Update Response ---- #
class UpdateSubjectResponse(BaseModel):
    id: UUID
    title: str
    code: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- Delete Response ---- #
class DeleteSubjectResponse(BaseModel):
    success: bool


# ---- Hard Delete Response ---- #
class HardDeleteSubjectResponse(BaseModel):
    success: bool


# ---- Restore Request ---- #
class RestoreSubjectRequest(BaseModel):
    reason: str | None = None


# ---- Restore Response ---- #
class RestoreSubjectResponse(BaseModel):
    id: UUID
    title: str
    code: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- Get Deleted Response ---- #
class GetDeletedSubjectResponse(BaseModel):
    id: UUID
    title: str
    code: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime