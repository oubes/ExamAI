# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, ForeignKey, Float, Index
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from pgvector.sqlalchemy import Vector

from src.infra.db.base import Base
from src.core.di.settings import get_settings


# ---- Settings ---- #
settings = get_settings()


# ---------- Models ---------- #

# ---- Knowledge Base ---- #
class KnowledgeBase(Base):
    # ---- Table Name ---- #
    __tablename__ = "knowledge_base"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    document_id: Mapped[int] = mapped_column(BigInteger)
    chunk_index: Mapped[int] = mapped_column(BigInteger, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(Text, default="text")
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.alibaba_embeddings_dim))

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_kb_subject_id", "subject_id"),
        Index("idx_kb_document_id", "document_id"),
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"KnowledgeBase("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"chunk_index={self.chunk_index}"
            f")"
        )