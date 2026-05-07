# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, Float, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Prompt Run / LLM Call ---- #
class PromptRun(Base):
    # ---- Table Name ---- #
    __tablename__ = "prompt_runs"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    model_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    prompt: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    response: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    token_usage: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)
    latency_ms: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_prompt_run_model_name", "model_name"),
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"PromptRun("
            f"id={self.id}, "
            f"model='{self.model_name}'"
            f")"
        )