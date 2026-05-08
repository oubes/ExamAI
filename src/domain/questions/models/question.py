# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

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
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("chapters.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("topics.id"), nullable=False)
    content: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    type: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    difficulty: Mapped[int] = mapped_column(__name_pos=Integer, default=1)
    importance: Mapped[int] = mapped_column(__name_pos=Integer, default=1)
    tags: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(__name_pos=Vector(settings.alibaba_embeddings_dim))
    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_subject_id", "subject_id"),
        Index("idx_question_chapter_id", "chapter_id"),
        Index("idx_question_topic_id", "topic_id"),
        Index("idx_question_search_vector", "search_vector", postgresql_using="gin"),
    )

    # ---- Relationships ---- #
    subject = relationship(argument="Subject", lazy="selectin")
    chapter = relationship(argument="Chapter", back_populates="questions", lazy="selectin")
    topic = relationship(argument="Topic", back_populates="questions", lazy="selectin")
    options = relationship(argument="QuestionOption", back_populates="question", lazy="selectin")
    model_answer = relationship(argument="ModelAnswer", back_populates="question", uselist=False, lazy="selectin")
    skill_links = relationship(argument="QuestionSkill", back_populates="question", lazy="selectin")

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