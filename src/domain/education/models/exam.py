# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Integer, ForeignKey, Index, Float

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Exam ---- #
class Exam(Base):
    # ---- Table Name ---- #
    __tablename__ = "exams"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    title: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    exam_type: Mapped[str] = mapped_column(__name_pos=Text, default="static")
    difficulty_profile: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)
    time_limit: Mapped[int] = mapped_column(__name_pos=Integer, default=0)
    scope_config: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_exam_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    subject = relationship(argument="Subject", back_populates="exams", lazy="selectin")
    questions = relationship(argument="Question", back_populates="exam", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Exam("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"type='{self.exam_type}'"
            f")"
        )