# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Integer, ForeignKey, Index, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Exam ---- #
class Exam(Base):
    # ---- Table Name ---- #
    __tablename__ = "exams"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    exam_type: Mapped[str] = mapped_column(Text, default="static")
    difficulty_profile: Mapped[float] = mapped_column(Float, default=1.0)
    time_limit: Mapped[int] = mapped_column(Integer, default=0)
    scope_config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_exam_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    subject = relationship("Subject", back_populates="exams", lazy="selectin")
    questions = relationship("Question", back_populates="exam", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Exam("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"type='{self.exam_type}'"
            f")"
        )