# ---- Imports ---- #
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from src.db.base import Base


# ---------- Models ---------- #

# ---- User ---- #
class User(Base):
    # ---- Table Name ---- #
    __tablename__ = "users"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    user_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False, unique=True)
    role: Mapped[str] = mapped_column(__name_pos=Text, nullable=False, default="user")
    email: Mapped[str] = mapped_column(__name_pos=Text, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(__name_pos=Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(__name_pos=Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(__name_pos=Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---- Relationships ---- #
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    attempts = relationship("ExamAttempt", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

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


# ---- User Session ---- #
class UserSession(Base):
    # ---- Table Name ---- #
    __tablename__ = "user_sessions"

    # ---- Columns ---- #
    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(__name_pos=ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(__name_pos=Boolean, default=True, nullable=False)

    ip_address: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(__name_pos=Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), nullable=False)

    # ---- Relationships ---- #
    user = relationship("User", back_populates="sessions", lazy="selectin")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"UserSession("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"is_active={self.is_active}, "
            f"ip_address='{self.ip_address}'"
            f")"
        )