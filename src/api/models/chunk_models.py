# ---- Imports ---- #
from uuid import UUID
from pydantic import BaseModel


# -------------------- Chunk -------------------- #

# ---- Create Chunk Request ---- #
class CreateChunkRequest(BaseModel):
    book_id: UUID
    subject_id: UUID
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    chunk_index: int
    content: str


# ---- Chunk Response ---- #
class ChunkResponse(BaseModel):
    id: UUID
    book_id: UUID
    subject_id: UUID
    chapter_id: UUID | None
    topic_id: UUID | None
    chunk_index: int
    content: str


# ---- List Response ---- #
class ListChunksResponse(BaseModel):
    items: list[ChunkResponse]


# ---- Update Request ---- #
class UpdateChunkRequest(BaseModel):
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    chunk_index: int | None = None
    content: str | None = None


# ---- Delete Response ---- #
class DeleteChunkResponse(BaseModel):
    success: bool