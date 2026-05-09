# ---- Imports ---- #
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Text, Boolean, func, Float
from sqlalchemy.dialects.postgresql import UUID

from src.infra.db.base import Base


# ---------- Models ---------- #

# ---- User ---- #
class User(Base):
    # ---- Table Name ---- #
    __tablename__ = "users"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    user_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False, unique=True)
    role: Mapped[str] = mapped_column(__name_pos=Text, default="user")
    email: Mapped[str] = mapped_column(__name_pos=Text, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(__name_pos=Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(__name_pos=Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(__name_pos=Boolean, default=False)
    global_learning_velocity: Mapped[float] = mapped_column(__name_pos=Float, default=0.0)
    preferred_difficulty_band: Mapped[float] = mapped_column(__name_pos=Float, default=1.0)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now())

    # ---- Relationships ---- #
    enrollments = relationship(argument="Enrollment", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    attempts = relationship(argument="ExamAttempt", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    sessions = relationship(argument="UserSession", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    uploads = relationship(argument="UploadFile", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"User("
            f"id={self.id}, "
            f"user_name='{self.user_name}', "
            f"email='{self.email}', "
            f"role='{self.role}', "
            f"is_active={self.is_active}, "
            f"is_verified={self.is_verified}"
            f")"
        )