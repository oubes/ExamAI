# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Feedback ---- #
class Feedback(Base):
    # ---- Table Name ---- #
    __tablename__ = "feedback"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("answers.id"), nullable=False)
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_score: Mapped[float] = mapped_column(BigInteger, default=0.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_feedback_answer_id", "answer_id"),
    )

    # ---- Relationships ---- #
    answer = relationship("Answer", back_populates="feedback", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self):
        return f"Feedback(id={self.id}, answer_id={self.answer_id}, quality_score={self.quality_score})"