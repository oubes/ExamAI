# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Subject ---- #
class Subject(Base):
    #--- Table Name ---- #
    __tablename__ = "subjects"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_subject_code", "code"),
    )

    # ---- Relationships ---- #
    chapters = relationship("Chapter", back_populates="subject", lazy="selectin")
    enrollments = relationship("Enrollment", back_populates="subject", lazy="selectin")
    exams = relationship("Exam", back_populates="subject", lazy="selectin")
    student_states = relationship("StudentSubjectState", back_populates="subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Subject("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"code='{self.code}'"
            f")"
        )