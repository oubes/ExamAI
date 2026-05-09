# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Chapter ---- #
class Chapter(Base):
    # ---- Table Name ---- #
    __tablename__ = "chapters"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(BigInteger, default=0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_chapter_subject_id", "subject_id"),
    )

    # ---- Relationships ---- #
    subject = relationship("Subject", lazy="selectin")
    topics = relationship("Topic", back_populates="chapter", lazy="selectin")
    questions = relationship("Question", back_populates="chapter", lazy="selectin")
    skills = relationship("Skill", back_populates="chapter", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Chapter("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"subject_id={self.subject_id}"
            f")"
        )