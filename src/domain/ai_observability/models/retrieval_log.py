# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Float, Text, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Retrieval Log ---- #
class RetrievalLog(Base):
    # ---- Table Name ---- #
    __tablename__ = "retrieval_logs"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    query: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    retrieval_type: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    retrieved_items: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    rerank_scores: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_retrieval_log_type", "retrieval_type"),
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"RetrievalLog("
            f"id={self.id}, "
            f"retrieval_type='{self.retrieval_type}'"
            f")"
        )