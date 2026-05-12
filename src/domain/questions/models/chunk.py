# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Chunk ---- #
class DocumentChunk(Base):

    # ---- Table Name ---- #
    __tablename__ = "document_chunks"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chapters.id"), nullable=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id"), nullable=True)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_chunk_book", "book_id"),
        Index("idx_chunk_subject", "subject_id"),
        Index("idx_chunk_chapter", "chapter_id"),
        Index("idx_chunk_topic", "topic_id"),
    )

    # ---- Relationships ---- #
    book = relationship("UploadFile", lazy="selectin")
    subject = relationship("Subject", lazy="selectin")
    chapter = relationship("Chapter", lazy="selectin")
    topic = relationship("Topic", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"DocumentChunk("
            f"id={self.id}, "
            f"book_id={self.book_id}, "
            f"chunk_index={self.chunk_index}, "
            f"subject_id={self.subject_id}, "
            f"chapter_id={self.chapter_id}, "
            f"topic_id={self.topic_id}"
            f")"
        )