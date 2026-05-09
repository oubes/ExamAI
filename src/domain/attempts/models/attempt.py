# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Numeric, DateTime, Text, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Exam Attempt ---- #
class ExamAttempt(Base):
    # ---- Table Name ---- #
    __tablename__ = "exam_attempts"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    final_score: Mapped[float] = mapped_column(Numeric, default=0.0)
    ai_score: Mapped[float] = mapped_column(Numeric, default=0.0)
    human_score: Mapped[float] = mapped_column(Numeric, default=0.0)
    status: Mapped[str] = mapped_column(Text, default="pending")
    duration_sec: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    generation_mode: Mapped[str] = mapped_column(Text, default="manual")
    adaptive_session_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("generated_exam_sessions.id"), nullable=True)
    completed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_attempt_user_id", "user_id"),
        Index("idx_attempt_exam_id", "exam_id"),
    )

    # ---- Relationships ---- #
    user = relationship("User", back_populates="attempts", lazy="selectin")
    answers = relationship("Answer", back_populates="attempt", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self):
        return f"ExamAttempt(id={self.id}, user_id={self.user_id}, exam_id={self.exam_id}, final_score={self.final_score})"