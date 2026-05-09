# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Topic ---- #
class Topic(Base):
    __tablename__ = "topics"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_weight: Mapped[float] = mapped_column(Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_topic_subject_id", "subject_id"),
        Index("idx_topic_chapter_id", "chapter_id"),
    )

    # ---- Relationships ---- #
    subject = relationship("Subject", lazy="selectin")
    chapter = relationship("Chapter", back_populates="topics", lazy="selectin")
    skills = relationship("Skill", back_populates="topic", lazy="selectin")
    questions = relationship("Question", back_populates="topic", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Topic("
            f"id={self.id}, "
            f"title='{self.title}'"
            f")"
        )