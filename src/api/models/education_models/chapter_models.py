# ---- Imports ---- #
from uuid import UUID
from pydantic import BaseModel


# -------------------- Chapter -------------------- #

# ---- Add Chapter Request ---- #
class AddChapterRequest(BaseModel):
    subject_id: UUID
    title: str
    description: str | None = None
    order_index: int = 0


# ---- Add Chapter Response ---- #
class AddChapterResponse(BaseModel):
    id: UUID
    subject_id: UUID
    title: str
    description: str | None
    order_index: int


# ---- Get Chapter Response ---- #
class GetChapterResponse(BaseModel):
    id: UUID
    subject_id: UUID
    title: str
    description: str | None
    order_index: int


# ---- List Chapters Response ---- #
class ListChaptersResponse(BaseModel):
    items: list[GetChapterResponse]


# ---- Update Chapter Request ---- #
class UpdateChapterRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    order_index: int | None = None


# ---- Update Chapter Response ---- #
class UpdateChapterResponse(BaseModel):
    id: UUID
    subject_id: UUID
    title: str
    description: str | None
    order_index: int


# ---- Delete Chapter Response ---- #
class DeleteChapterResponse(BaseModel):
    success: bool
