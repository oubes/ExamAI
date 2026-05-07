# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Integer, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Exams ---- #
class Exam(Base):

    # ---- Table Name ---- #
    __tablename__ = "exams"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    title: Mapped[str] = mapped_column(Text)
    time_limit: Mapped[int] = mapped_column(Integer)

    # ---- Indexes ---- #
    __table_args__ = (Index("idx_exam_subject_id", "subject_id"),)

    # ---- Relationships ---- #
    subject = relationship("Subject", back_populates="exams", lazy="selectin")
    questions = relationship("Question", back_populates="exam", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Exam("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"title='{self.title}', "
            f"time_limit={self.time_limit}"
            f")"
        )