# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Enrollment ---- #
class Enrollment(Base):
    # ---- Table Name ---- #
    __tablename__ = "enrollments"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_enrollment_user_id", "user_id"),
        Index("idx_enrollment_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    user = relationship("User", back_populates="enrollments", lazy="selectin")
    subject = relationship("Subject", back_populates="enrollments", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self):
        return (
            f"Enrollment("
            f"user_id={self.user_id}, "
            f"subject_id={self.subject_id}"
            f")"
        )