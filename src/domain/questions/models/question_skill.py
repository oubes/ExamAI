# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Question Skill ---- #
class QuestionSkill(Base):
    # ---- Table Name ---- #
    __tablename__ = "question_skills"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id"), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_skill_question_id", "question_id"),
        Index("idx_question_skill_skill_id", "skill_id"),
    )

    # ---- Relationships ---- #
    question = relationship("Question", back_populates="skill_links", lazy="selectin")
    skill = relationship("Skill", back_populates="skill_questions", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"QuestionSkill("
            f"question_id={self.question_id}, "
            f"skill_id={self.skill_id}, "
            f"weight={self.weight}"
            f")"
        )