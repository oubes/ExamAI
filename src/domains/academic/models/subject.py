# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Subjects ---- #
class Subject(Base):

    # ---- Table Name ---- #
    __tablename__ = "subjects"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    code: Mapped[str] = mapped_column(Text)

    # ---- Indexes ---- #
    __table_args__ = (Index("idx_subject_code", "code"),)

    # ---- Relationships ---- #
    exams = relationship("Exam", back_populates="subject", lazy="selectin")
    enrollments = relationship("Enrollment", back_populates="subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Subject("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"code='{self.code}'"
            f")"
        )