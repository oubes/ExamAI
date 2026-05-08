# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Float, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Grading Rubric ---- #
class GradingRubric(Base):
    # ---- Table Name ---- #
    __tablename__ = "grading_rubrics"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("questions.id"), nullable=False)
    criterion: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    description: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    max_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    weight: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_grading_rubric_question_id", "question_id"),
    )

    # ---- Relationships ---- #
    question = relationship(argument="Question", lazy="selectin")
    rubric_results = relationship(argument="RubricResult", back_populates="rubric", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"GradingRubric("
            f"id={self.id}, "
            f"question_id={self.question_id}, "
            f"criterion='{self.criterion}'"
            f")"
        )