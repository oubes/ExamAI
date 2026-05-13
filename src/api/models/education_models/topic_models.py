# ---- Imports ---- #
from uuid import UUID
from pydantic import BaseModel


# -------------------- Topic -------------------- #

# ---- Add Topic Request ---- #
class AddTopicRequest(BaseModel):
    subject_id: UUID
    chapter_id: UUID
    title: str
    description: str | None = None
    difficulty_weight: float = 1.0


# ---- Add Topic Response ---- #
class AddTopicResponse(BaseModel):
    id: UUID
    subject_id: UUID
    chapter_id: UUID
    title: str
    description: str | None
    difficulty_weight: float


# ---- Get Topic Response ---- #
class GetTopicResponse(BaseModel):
    id: UUID
    subject_id: UUID
    chapter_id: UUID
    title: str
    description: str | None
    difficulty_weight: float


# ---- List Topics Response ---- #
class ListTopicsResponse(BaseModel):
    items: list[GetTopicResponse]


# ---- Update Topic Request ---- #
class UpdateTopicRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty_weight: float | None = None


# ---- Update Topic Response ---- #
class UpdateTopicResponse(BaseModel):
    id: UUID
    subject_id: UUID
    chapter_id: UUID
    title: str
    description: str | None
    difficulty_weight: float


# ---- Delete Topic Response ---- #
class DeleteTopicResponse(BaseModel):
    success: bool