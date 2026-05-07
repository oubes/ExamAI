# ---- Imports ---- #
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- Upload File ---- #
class UploadFileModel(Base):

    # ---- Table Name ---- #
    __tablename__ = "uploads"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        __name_pos=UUID(as_uuid=True),
        __type_pos=ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False
    )
    category: Mapped[str] = mapped_column(__name_pos=String, nullable=False)
    original_name: Mapped[str] = mapped_column(__name_pos=String, nullable=False)
    stored_name: Mapped[str] = mapped_column(__name_pos=String, nullable=False)
    path: Mapped[str] = mapped_column(__name_pos=String, nullable=False)
    content_type: Mapped[str | None] = mapped_column(__name_pos=String, nullable=True)
    size: Mapped[int | None] = mapped_column(__name_pos=Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # ---- Relationships ---- #
    user = relationship(argument="User", back_populates="uploads", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"UploadFileModel("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"original_name='{self.original_name}', "
            f"stored_name='{self.stored_name}', "
            f"path='{self.path}', "
            f"size={self.size}"
            f")"
        )