# ---- Imports ---- #
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---- Upload Response ---- #
class UploadResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID

    category: str

    original_name: str
    stored_name: str

    path: str
    content_type: str

    size: int

    processing_status: str
    processing_error: str | None

    is_processed: bool

    created_at: datetime


# ---- Delete Upload Response ---- #
class DeleteUploadResponse(BaseModel):
    deleted: bool


# ---- Upload Stats Response ---- #
class UploadStatsResponse(BaseModel):
    total: int
    processed: int
    failed: int