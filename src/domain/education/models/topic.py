# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Float, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Topic ---- #
class Topic(Base):
    # ---- Table Name ---- #
    __tablename__ = "topics"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    chapter_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("chapters.id"), nullable=False)

    title: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    description: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    difficulty_weight: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_topic_subject_id", "subject_id"),
        Index("idx_topic_chapter_id", "chapter_id"),
    )

    # ---- Relationships ---- #
    subject = relationship(argument="Subject", lazy="selectin")

    chapter = relationship(
        argument="Chapter",
        back_populates="topics",
        lazy="selectin"
    )

    skills = relationship(
        argument="Skill",
        back_populates="topic",
        lazy="selectin"
    )

    questions = relationship(
        argument="Question",
        back_populates="topic",
        lazy="selectin"
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Topic("
            f"id={self.id}, "
            f"title='{self.title}'"
            f")"
        )