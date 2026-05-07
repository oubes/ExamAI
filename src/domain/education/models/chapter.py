# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Chapter ---- #
class Chapter(Base):
    # ---- Table Name ---- #
    __tablename__ = "chapters"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)

    title: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)

    description: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    order_index: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_chapter_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    subject = relationship(argument="Subject", lazy="selectin")

    topics = relationship(argument="Topic", back_populates="chapter", lazy="selectin")

    questions = relationship(argument="Question", back_populates="chapter", lazy="selectin")

    skills = relationship(argument="Skill", back_populates="chapter", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Chapter("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"subject_id={self.subject_id}"
            f")"
        )