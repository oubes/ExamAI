# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Student Subject State ---- #
class StudentSubjectState(Base):
    # ---- Table Name ---- #
    __tablename__ = "student_subject_states"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)

    mastery_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    consistency_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    retention_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    reasoning_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    speed_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    engagement_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    current_difficulty: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)
    recommended_difficulty: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)

    learning_velocity: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    forgetting_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    total_attempts: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)
    total_correct_answers: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)

    weak_topics: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    strong_topics: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    learning_style: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    last_difficulty_shift: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    needs_help: Mapped[bool] = mapped_column(__name_pos=Float, default=False)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_student_subject_state_user_id", "user_id"),
        Index("idx_student_subject_state_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", lazy="selectin")
    subject = relationship(argument="Subject", lazy="selectin")
    skills = relationship(argument="SkillState", back_populates="student_state", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"StudentSubjectState("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}, "
            f"mastery_score={self.mastery_score}"
            f")"
        )