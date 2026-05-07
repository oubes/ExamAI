# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Question Skill ---- #
class QuestionSkill(Base):
    # ---- Table Name ---- #
    __tablename__ = "question_skills"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    question_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("questions.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("skills.id"), nullable=False)

    weight: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_skill_question_id", "question_id"),
        Index("idx_question_skill_skill_id", "skill_id"),
    )

    # ---- Relationships ---- #
    question = relationship(
        argument="Question",
        back_populates="skill_links",
        lazy="selectin"
    )

    skill = relationship(
        argument="Skill",
        back_populates="skill_questions",
        lazy="selectin"
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"QuestionSkill("
            f"question_id={self.question_id}, "
            f"skill_id={self.skill_id}, "
            f"weight={self.weight}"
            f")"
        )