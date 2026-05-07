# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Numeric, Float, Boolean, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Answer ---- #
class Answer(Base):
    # ---- Table Name ---- #
    __tablename__ = "answers"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("exam_attempts.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("questions.id"), nullable=False)
    option_id: Mapped[int | None] = mapped_column(__name_pos=ForeignKey("question_options.id"), nullable=True)
    student_answer: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    time_spent_sec: Mapped[int | None] = mapped_column(__name_pos=BigInteger, nullable=True)
    partial_credit: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    is_correct: Mapped[bool] = mapped_column(__name_pos=Boolean, default=False)

    # ---- HITL ---- #
    needs_review: Mapped[bool] = mapped_column(__name_pos=Boolean, default=False)
    reviewed_by_human: Mapped[bool] = mapped_column(__name_pos=Boolean, default=False)
    human_override_score: Mapped[float | None] = mapped_column(__name_pos=Float, nullable=True)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_answer_attempt_id", "attempt_id"),
        Index("idx_answer_question_id", "question_id"),
    )

    # ---- Relationships ---- #
    attempt = relationship(argument="ExamAttempt", back_populates="answers", lazy="selectin")
    question = relationship(argument="Question", lazy="selectin")
    option = relationship(argument="QuestionOption", lazy="selectin")
    feedback = relationship(argument="Feedback", back_populates="answer", uselist=False, lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Answer("
            f"id={self.id}, "
            f"attempt_id={self.attempt_id}, "
            f"question_id={self.question_id}, "
            f"score={self.score}, "
            f"is_correct={self.is_correct}"
            f")"
        )