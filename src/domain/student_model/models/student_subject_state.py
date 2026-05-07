# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Student Subject State ---- #
class StudentSubjectState(Base):
    # ---- Table Name ---- #
    __tablename__ = "student_subject_state"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)

    # ---- Core Learning Metrics ---- #
    mastery_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    stability_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    speed_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    accuracy_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    # ---- Difficulty Modeling ---- #
    preferred_difficulty: Mapped[int] = mapped_column(__name_pos=Float, default=1.0)
    max_sustainable_difficulty: Mapped[int] = mapped_column(__name_pos=Float, default=1.0)

    # ---- Behavior Signals ---- #
    engagement_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    fatigue_level: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    # ---- Temporal Tracking ---- #
    last_updated: Mapped[DateTime] = mapped_column(
        __name_pos=DateTime(timezone=True),
        server_default=func.now()
    )

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_student_state_user_subject", "user_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", back_populates="subject_states", lazy="selectin")
    subject = relationship(argument="Subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"StudentSubjectState("
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}, "
            f"mastery={self.mastery_score}, "
            f"accuracy={self.accuracy_score}"
            f")"
        )