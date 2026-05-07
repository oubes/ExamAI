# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, DateTime, Numeric, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Exam Attempt ---- #
class ExamAttempt(Base):
    # ---- Table Name ---- #
    __tablename__ = "exam_attempts"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    status: Mapped[str] = mapped_column(__name_pos=Text, default="in_progress")
    final_score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
    ai_score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
    human_score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
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
        Index("idx_attempt_user_id", "user_id"),
        Index("idx_attempt_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", back_populates="attempts", lazy="selectin")
    answers = relationship(argument="Answer", back_populates="attempt", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"ExamAttempt("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}, "
            f"status={self.status}"
            f")"
        )