# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Student Analytics Snapshot ---- #
class StudentAnalyticsSnapshot(Base):
    # ---- Table Name ---- #
    __tablename__ = "student_analytics_snapshots"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    avg_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    mastery_score: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    improvement_rate: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    weakest_skill: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    strongest_skill: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    snapshot_date: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_student_snapshot_user_id", "user_id"),
        Index("idx_student_snapshot_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", lazy="selectin")
    subject = relationship(argument="Subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"StudentAnalyticsSnapshot("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"mastery_score={self.mastery_score}"
            f")"
        )