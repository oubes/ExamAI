# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Boolean, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Question Option ---- #
class QuestionOption(Base):
    # ---- Table Name ---- #
    __tablename__ = "question_options"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(__name_pos=Boolean, default=False)
    order: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_option_question_id", "question_id"),
    )

    # ---- Relationships ---- #
    question = relationship(argument="Question", back_populates="options", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"QuestionOption("
            f"id={self.id}, "
            f"question_id={self.question_id}, "
            f"is_correct={self.is_correct}"
            f")"
        )