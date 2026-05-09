# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Numeric, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Answer ---- #
class Answer(Base):
    # ---- Table Name ---- #
    __tablename__ = "answers"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_attempts.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    option_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("question_options.id"), nullable=True)
    student_answer: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Numeric, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    time_spent_sec: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    partial_credit: Mapped[float] = mapped_column(Float, default=0.0)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    # ---- HITL ---- #
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by_human: Mapped[bool] = mapped_column(Boolean, default=False)
    human_override_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_answer_attempt_id", "attempt_id"),
        Index("idx_answer_question_id", "question_id"),
    )

    # ---- Relationships ---- #
    attempt = relationship("ExamAttempt", back_populates="answers", lazy="selectin")
    question = relationship("Question", lazy="selectin")
    option = relationship("QuestionOption", lazy="selectin")
    feedback = relationship("Feedback", back_populates="answer", uselist=False, lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self):
        return f"Answer(id={self.id}, attempt_id={self.attempt_id}, question_id={self.question_id}, score={self.score}, is_correct={self.is_correct})"