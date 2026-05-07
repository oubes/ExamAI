# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Float, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Skill ---- #
class Skill(Base):
    # ---- Table Name ---- #
    __tablename__ = "skills"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("chapters.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("topics.id"), nullable=False)

    name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    description: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    importance_weight: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_skill_subject_id", "subject_id"),
        Index("idx_skill_chapter_id", "chapter_id"),
        Index("idx_skill_topic_id", "topic_id"),
    )

    # ---- Relationships ---- #
    subject = relationship(argument="Subject", lazy="selectin")

    chapter = relationship(
        argument="Chapter",
        lazy="selectin"
    )

    topic = relationship(
        argument="Topic",
        back_populates="skills",
        lazy="selectin"
    )

    skill_questions = relationship(
        argument="QuestionSkill",
        back_populates="skill",
        lazy="selectin"
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Skill("
            f"id={self.id}, "
            f"name='{self.name}'"
            f")"
        )