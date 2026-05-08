# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Rubric Result ---- #
class RubricResult(Base):
    # ---- Table Name ---- #
    __tablename__ = "rubric_results"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    answer_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("answers.id"), nullable=False)
    rubric_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("grading_rubrics.id"), nullable=False)
    assigned_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    reasoning: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_rubric_result_answer_id", "answer_id"),
        Index("idx_rubric_result_rubric_id", "rubric_id"),
    )

    # ---- Relationships ---- #
    answer = relationship(argument="Answer", lazy="selectin")
    rubric = relationship(argument="GradingRubric", back_populates="rubric_results", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"RubricResult("
            f"id={self.id}, "
            f"answer_id={self.answer_id}, "
            f"assigned_score={self.assigned_score}"
            f")"
        )