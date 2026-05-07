# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Feedback ---- #
class Feedback(Base):
    # ---- Table Name ---- #
    __tablename__ = "feedback"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    answer_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("answers.id"), nullable=False)
    feedback_text: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    quality_score: Mapped[float] = mapped_column(__name_pos=BigInteger, default=0.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_feedback_answer_id", "answer_id"),
    )

    # ---- Relationships ---- #
    answer = relationship(argument="Answer", back_populates="feedback", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Feedback("
            f"id={self.id}, "
            f"answer_id={self.answer_id}, "
            f"quality_score={self.quality_score}"
            f")"
        )