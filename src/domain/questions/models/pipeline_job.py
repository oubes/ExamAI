# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Pipeline Job ---- #
class PipelineJob(Base):

    # ---- Table Name ---- #
    __tablename__ = "pipeline_jobs"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id"),
        nullable=False
    )

    current_chunk: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    total_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[str] = mapped_column(String, default="running", nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_pipeline_job_book", "book_id"),
        Index("idx_pipeline_job_subject", "subject_id"),
        Index("idx_pipeline_job_status", "status"),
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"PipelineJob("
            f"id={self.id}, "
            f"book_id={self.book_id}, "
            f"subject_id={self.subject_id}, "
            f"current_chunk={self.current_chunk}, "
            f"total_chunks={self.total_chunks}, "
            f"status='{self.status}'"
            f")"
        )