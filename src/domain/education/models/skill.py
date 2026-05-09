# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Skill ---- #
class Skill(Base):
    # ---- Table Name ---- #
    __tablename__ = "skills"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance_weight: Mapped[float] = mapped_column(Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_skill_subject_id", "subject_id"),
        Index("idx_skill_chapter_id", "chapter_id"),
        Index("idx_skill_topic_id", "topic_id"),
    )

    # ---- Relationships ---- #
    subject = relationship("Subject", lazy="selectin")
    chapter = relationship("Chapter", lazy="selectin")
    topic = relationship("Topic", back_populates="skills", lazy="selectin")
    skill_questions = relationship("QuestionSkill", back_populates="skill", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Skill("
            f"id={self.id}, "
            f"name='{self.name}'"
            f")"
        )