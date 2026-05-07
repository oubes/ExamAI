# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Float, Text, ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Adaptation Event ---- #
class AdaptationEvent(Base):
    # ---- Table Name ---- #
    __tablename__ = "adaptation_events"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), nullable=False)
    old_difficulty: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    new_difficulty: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    reason: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    trigger_source: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_adaptation_event_user_id", "user_id"),
        Index("idx_adaptation_event_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", lazy="selectin")
    subject = relationship(argument="Subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"AdaptationEvent("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"old_difficulty={self.old_difficulty}, "
            f"new_difficulty={self.new_difficulty}"
            f")"
        )