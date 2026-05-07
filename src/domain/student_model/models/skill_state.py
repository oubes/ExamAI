# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Float, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Skill State ---- #
class SkillState(Base):
    # ---- Table Name ---- #
    __tablename__ = "skill_state"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    mastery: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    retention: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    error_rate: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    improvement_rate: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    last_updated: Mapped[DateTime] = mapped_column(
        __name_pos=DateTime(timezone=True),
        server_default=func.now()
    )

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_skill_state_user_subject", "user_id", "subject_id"),
        Index("idx_skill_state_skill_name", "skill_name"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", lazy="selectin")
    subject = relationship(argument="Subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"SkillState("
            f"user_id={self.user_id}, "
            f"skill='{self.skill_name}', "
            f"mastery={self.mastery}, "
            f"confidence={self.confidence}"
            f")"
        )