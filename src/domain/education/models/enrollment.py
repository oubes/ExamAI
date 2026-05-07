# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func, Index

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Enrollment ---- #
class Enrollment(Base):
    # ---- Table Name ---- #
    __tablename__ = "enrollments"

    # ---- Columns ---- #
    user_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("users.id"), primary_key=True)
    subject_id: Mapped[int] = mapped_column(__name_pos=ForeignKey("subjects.id"), primary_key=True)

    created_at: Mapped[DateTime] = mapped_column(
        __name_pos=DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_enrollment_user_id", "user_id"),
        Index("idx_enrollment_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship(argument="User", back_populates="enrollments", lazy="selectin")
    subject = relationship(argument="Subject", back_populates="enrollments", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Enrollment("
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}"
            f")"
        )