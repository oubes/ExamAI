# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, DateTime, ForeignKey, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Learning Session ---- #
class LearningSession(Base):
    # ---- Table Name ---- #
    __tablename__ = "learning_sessions"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    start_time: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[DateTime | None] = mapped_column(__name_pos=DateTime(timezone=True), nullable=True)
    engagement_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    focus_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    productivity_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_learning_session_user_id", "user_id"),
        Index("idx_learning_session_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", lazy="selectin")
    subject = relationship(argument="Subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"LearningSession("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}"
            f")"
        )