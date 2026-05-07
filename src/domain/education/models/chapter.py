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
    order: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_chapter_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    subject = relationship(argument="Subject", back_populates="chapters", lazy="selectin")
    questions = relationship(argument="Question", back_populates="chapter", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Chapter("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"title='{self.title}', "
            f"order={self.order}"
            f")"
        )