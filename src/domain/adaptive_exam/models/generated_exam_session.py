# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Generated Exam Session ---- #
class GeneratedExamSession(Base):
    # ---- Table Name ---- #
    __tablename__ = "generated_exam_sessions"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    target_difficulty: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)
    generation_strategy: Mapped[str] = mapped_column(
        __name_pos=Text,
        default="adaptive"
    )
    estimated_mastery: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    started_at: Mapped[DateTime] = mapped_column(
        __name_pos=DateTime(timezone=True),
        server_default=func.now()
    )
    completed_at: Mapped[DateTime | None] = mapped_column(
        __name_pos=DateTime(timezone=True),
        nullable=True
    )

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_generated_exam_user_id", "user_id"),
        Index("idx_generated_exam_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(
        argument="User",
        lazy="selectin"
    )

    subject = relationship(
        argument="Subject",
        lazy="selectin"
    )

    questions = relationship(
        argument="GeneratedExamQuestion",
        back_populates="session",
        lazy="selectin"
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"GeneratedExamSession("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}"
            f")"
        )