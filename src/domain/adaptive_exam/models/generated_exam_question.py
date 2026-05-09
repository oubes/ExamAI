# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Generated Exam Question ---- #
class GeneratedExamQuestion(Base):
    # ---- Table Name ---- #
    __tablename__ = "generated_exam_questions"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generated_exam_sessions.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    question_order: Mapped[int] = mapped_column(default=0)
    selection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    predicted_difficulty_fit: Mapped[float] = mapped_column(Float, default=0.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_generated_exam_question_session_id", "session_id"),
        Index("idx_generated_exam_question_question_id", "question_id"),
    )

    # ---- Relationships ---- #
    session = relationship("GeneratedExamSession", back_populates="questions", lazy="selectin")
    question = relationship("Question", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self):
        return f"GeneratedExamQuestion(id={self.id}, session_id={self.session_id}, question_id={self.question_id})"