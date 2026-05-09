# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Generated Exam Question ---- #
class GeneratedExamQuestion(Base):
    # ---- Table Name ---- #
    __tablename__ = "generated_exam_questions"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    session_id: Mapped[int] = mapped_column(
        __name_pos=ForeignKey("generated_exam_sessions.id"),
        nullable=False
    )

    knowledge_base_id: Mapped[int | None] = mapped_column(
        __name_pos=ForeignKey("knowledge_base.id"),
        nullable=True
    )

    question_id: Mapped[int] = mapped_column(
        __name_pos=ForeignKey("questions.id"),
        nullable=False
    )

    question_order: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)

    selection_reason: Mapped[str | None] = mapped_column(
        __name_pos=Text,
        nullable=True
    )

    predicted_difficulty_fit: Mapped[float] = mapped_column(
        __name_pos=Float,
        default=0.0
    )

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_generated_exam_question_session_id", "session_id"),
        Index("idx_generated_exam_question_question_id", "question_id"),
        Index("idx_generated_exam_question_chunk_id", "knowledge_base_id"),
    )

    # ---- Relationships ---- #
    session = relationship(argument="GeneratedExamSession", back_populates="questions", lazy="selectin")
    chunk = relationship(argument="KnowledgeBase", back_populates="generated_questions", lazy="selectin")
    question = relationship(argument="Question", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"GeneratedExamQuestion("
            f"id={self.id}, "
            f"session_id={self.session_id}, "
            f"question_id={self.question_id}"
            f")"
        )