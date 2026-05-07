# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, Float, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Agent Decision Log ---- #
class AgentDecisionLog(Base):
    # ---- Table Name ---- #
    __tablename__ = "agent_decision_logs"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    agent_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    context_type: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    input_state: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    decision: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_agent_decision_agent_name", "agent_name"),
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"AgentDecisionLog("
            f"id={self.id}, "
            f"agent='{self.agent_name}', "
            f"decision='{self.decision}'"
            f")"
        )