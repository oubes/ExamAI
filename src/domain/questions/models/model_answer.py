# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Model Answer ---- #
class ModelAnswer(Base):
    # ---- Table Name ---- #
    __tablename__ = "model_answers"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False,
        unique=True
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)

    # ---- Relationships ---- #
    question = relationship(
        "Question",
        back_populates="model_answer",
        lazy="selectin"
    )

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Answer("
            f"id={self.id}, "
            f"question_id={self.question_id}"
            f")"
        )