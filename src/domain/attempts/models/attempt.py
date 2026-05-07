# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Numeric, DateTime, Text, ForeignKey, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Exam Attempt ---- #
class ExamAttempt(Base):
    # ---- Table Name ---- #
    __tablename__ = "exam_attempts"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    exam_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("exams.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    final_score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
    ai_score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
    human_score: Mapped[float] = mapped_column(__name_pos=Numeric, default=0.0)
    status: Mapped[str] = mapped_column(__name_pos=Text, default="pending")
    duration_sec: Mapped[int | None] = mapped_column(__name_pos=BigInteger, nullable=True)
    generation_mode: Mapped[str] = mapped_column(__name_pos=Text, default="manual")
    adaptive_session_id: Mapped[int | None] = mapped_column(__name_pos=ForeignKey("generated_exam_sessions.id"), nullable=True)
    completed_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_attempt_user_id", "user_id"),
        Index("idx_attempt_exam_id", "exam_id"),
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
            f"exam_id={self.exam_id}, "
            f"final_score={self.final_score}"
            f")"
        )