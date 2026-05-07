# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Enrollments ---- #
class Enrollment(Base):

    # ---- Table Name ---- #
    __tablename__ = "enrollments"

    # ---- Columns ---- #
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), primary_key=True)

    # ---- Relationships ---- #
    user = relationship("User", back_populates="enrollments", lazy="selectin")
    subject = relationship("Subject", back_populates="enrollments", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Enrollment("
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}"
            f")"
        )