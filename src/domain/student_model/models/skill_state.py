# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Skill State ---- #
class SkillState(Base):
    # ---- Table Name ---- #
    __tablename__ = "skill_states"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)

    student_state_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("student_subject_states.id"), nullable=False)

    skill_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("skills.id"), nullable=False)

    mastery_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    retention_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    attempts_count: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)
    success_count: Mapped[int] = mapped_column(__name_pos=BigInteger, default=0)

    avg_response_time: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)

    last_practiced_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_skill_state_student_state_id", "student_state_id"),
        Index("idx_skill_state_skill_id", "skill_id"),
    )

    # ---- Relationships ---- #
    student_state = relationship(argument="StudentSubjectState", back_populates="skills", lazy="selectin")

    skill = relationship(argument="Skill", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"SkillState("
            f"id={self.id}, "
            f"skill_id={self.skill_id}, "
            f"mastery_score={self.mastery_score}"
            f")"
        )