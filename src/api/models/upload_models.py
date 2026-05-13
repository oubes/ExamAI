# ---- Imports ---- #
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---- Upload Path Params ---- #
class UploadCategoryPath(BaseModel):
    category: str


class UploadFilePath(BaseModel):
    file_id: uuid.UUID


# ---- Query Params ---- #
class UploadListQuery(BaseModel):
    category: str | None = None
    limit: int = 50
    offset: int = 0


# ---- Upload Request (Multipart wrapper) ---- #
class UploadFileRequest(BaseModel):
    file: bytes  # NOTE: conceptual model (FastAPI still uses UploadFile)


# ---- Responses ---- #
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


class DeleteUploadResponse(BaseModel):
    deleted: bool


class UploadStatsResponse(BaseModel):
    total: int
    processed: int
    failed: int