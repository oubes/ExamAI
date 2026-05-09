# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID

from pgvector.sqlalchemy import Vector

from src.infra.db.base import Base
from src.core.di.settings import get_settings


# ---- Settings ---- #
settings = get_settings()


# ---------- Models ---------- #

# ---- Question ---- #
class Question(Base):
    # ---- Table Name ---- #
    __tablename__ = "questions"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    importance: Mapped[int] = mapped_column(Integer, default=1)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.alibaba_embeddings_dim))
    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_subject_id", "subject_id"),
        Index("idx_question_chapter_id", "chapter_id"),
        Index("idx_question_topic_id", "topic_id"),
        Index("idx_question_search_vector", "search_vector", postgresql_using="gin"),
    )

    # ---- Relationships ---- #
    subject = relationship("Subject", lazy="selectin")
    chapter = relationship("Chapter", back_populates="questions", lazy="selectin")
    topic = relationship("Topic", back_populates="questions", lazy="selectin")
    options = relationship("QuestionOption", back_populates="question", lazy="selectin")
    model_answer = relationship("ModelAnswer", back_populates="question", uselist=False, lazy="selectin")
    skill_links = relationship("QuestionSkill", back_populates="question", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Question("
            f"id={self.id}, "
            f"type='{self.type}', "
            f"difficulty={self.difficulty}, "
            f"importance={self.importance}"
            f")"
        )