# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Subject ---- #
class Subject(Base):
    # ---- Table Name ---- #
    __tablename__ = "subjects"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    code: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_subject_code", "code"),
    )

    # ---- Relationships ---- #
    chapters = relationship(argument="Chapter", back_populates="subject", lazy="selectin")
    enrollments = relationship(argument="Enrollment", back_populates="subject", lazy="selectin")
    exams = relationship(argument="Exam", back_populates="subject", lazy="selectin")
    student_states = relationship(argument="StudentSubjectState", back_populates="subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Subject("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"code='{self.code}'"
            f")"
        )