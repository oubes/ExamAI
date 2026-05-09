# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector

from src.infra.db.base import Base
from src.core.di.settings import get_settings


# ---- Settings ---- #
settings = get_settings()


# ---------- Models ---------- #

# ---- Questions ---- #
class Question(Base):

    # ---- Table Name ---- #
    __tablename__ = "questions"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)
    search_text: Mapped[str] = mapped_column(Text, default="")

    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.alibaba_embeddings_dim)
    )

    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_exam_id", "exam_id"),
        Index("idx_question_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "idx_question_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )

    # ---- Relationships ---- #
    exam = relationship("Exam", back_populates="questions", lazy="selectin")
    options = relationship("QuestionOption", back_populates="question", lazy="selectin")

    model_answer = relationship(
        "ModelAnswer",
        back_populates="question",
        uselist=False,
        lazy="selectin",
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Question("
            f"id={self.id}, "
            f"exam_id={self.exam_id}, "
            f"type='{self.type}'"
            f")"
        )


# ---- Question Options ---- #
class QuestionOption(Base):

    # ---- Table Name ---- #
    __tablename__ = "question_options"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    option_text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_option_question_id", "question_id"),
        Index(
            "idx_option_text_trgm",
            "option_text",
            postgresql_using="gin",
            postgresql_ops={"option_text": "gin_trgm_ops"},
        ),
    )

    # ---- Relationships ---- #
    question = relationship("Question", back_populates="options", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"QuestionOption("
            f"id={self.id}, "
            f"question_id={self.question_id}, "
            f"is_correct={self.is_correct}"
            f")"
        )


# ---- Model Answers ---- #
class ModelAnswer(Base):

    # ---- Table Name ---- #
    __tablename__ = "model_answers"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    content: Mapped[str] = mapped_column(Text)
    rubric: Mapped[dict] = mapped_column(Text)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.alibaba_embeddings_dim)
    )

    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_model_answer_question_id", "question_id"),
        Index("idx_model_answer_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "idx_model_answer_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )

    # ---- Relationships ---- #
    question = relationship("Question", back_populates="model_answer", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"ModelAnswer("
            f"id={self.id}, "
            f"question_id={self.question_id}"
            f")"
        )