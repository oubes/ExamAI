# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, ForeignKey, Index, Float
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
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    document_id: Mapped[int] = mapped_column(BigInteger)
    chunk_index: Mapped[int] = mapped_column(BigInteger, default=0)

    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[str] = mapped_column(Text, nullable=True)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.alibaba_embeddings_dim)
    )

    search_vector = mapped_column(TSVECTOR)

    source_type: Mapped[str] = mapped_column(Text)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0)

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
            f"content='{self.content[:50]}...'"
            f")"
        )