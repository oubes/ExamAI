# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, ForeignKey, Float, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

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
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[int | None] = mapped_column(__name_pos=ForeignKey("chapters.id"), nullable=True)
    document_id: Mapped[int] = mapped_column(__name_pos=BigInteger)
    chunk_index: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)
    content: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    source_type: Mapped[str] = mapped_column(__name_pos=Text, default="text")
    quality_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    importance_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    # ---- Retrieval ---- #
    embedding: Mapped[list[float]] = mapped_column(
        __name_pos=Vector(settings.alibaba_embeddings_dim)
    )

    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_kb_subject_id", "subject_id"),
        Index("idx_kb_document_id", "document_id"),
        Index("idx_kb_search_vector", "search_vector", postgresql_using="gin"),
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