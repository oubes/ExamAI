# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Grading Run ---- #
class GradingRun(Base):
    # ---- Table Name ---- #
    __tablename__ = "grading_runs"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    answer_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("answers.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    token_usage: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_grading_run_answer_id", "answer_id"),
        Index("idx_grading_run_model_name", "model_name"),
    )

    # ---- Relationships ---- #
    answer = relationship(
        argument="Answer",
        lazy="selectin"
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"GradingRun("
            f"id={self.id}, "
            f"answer_id={self.answer_id}, "
            f"model_name='{self.model_name}'"
            f")"
        )