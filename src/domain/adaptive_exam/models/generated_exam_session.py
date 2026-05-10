# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Text, ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Generated Exam Session ---- #
class GeneratedExamSession(Base):
    # ---- Table Name ---- #
    __tablename__ = "generated_exam_sessions"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    target_difficulty: Mapped[float] = mapped_column(Float, default=1.0)
    generation_strategy: Mapped[str] = mapped_column(Text, default="adaptive")
    estimated_mastery: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_generated_exam_user_id", "user_id"),
        Index("idx_generated_exam_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship("User", lazy="selectin")
    subject = relationship("Subject", lazy="selectin")
    questions = relationship("GeneratedExamQuestion", back_populates="session", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self):
        return f"GeneratedExamSession(id={self.id}, user_id={self.user_id}, subject_id={self.subject_id})"