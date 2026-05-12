# ---- Imports ---- #
import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Index, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Subject ---- #
class Subject(Base):
    #--- Table Name ---- #
    __tablename__ = "subjects"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_subject_code", "code"),
        UniqueConstraint("code", name="uq_subject_code"),
        Index("idx_subject_active", "is_active"),
    )

    # ---- Relationships ---- #
    chapters = relationship("Chapter", back_populates="subject", lazy="selectin")
    enrollments = relationship("Enrollment", back_populates="subject", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Subject("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"code='{self.code}', "
            f"is_active={self.is_active}"
            f")"
        )