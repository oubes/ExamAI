# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Question Option ---- #
class QuestionOption(Base):
    # ---- Table Name ---- #
    __tablename__ = "question_options"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(default=0)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_option_question_id", "question_id"),
    )

    # ---- Relationships ---- #
    question = relationship("Question", back_populates="options", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"QuestionOption("
            f"id={self.id}, "
            f"question_id={self.question_id}, "
            f"is_correct={self.is_correct}"
            f")"
        )