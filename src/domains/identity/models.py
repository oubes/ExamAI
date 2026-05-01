# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, DateTime, Text, Boolean, func
from src.db.base import Base


# ---------- Models ---------- #

# ---- User ---- #
class User(Base):
    # ---- Table Name ---- #
    __tablename__ = "users"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(__name_pos=BigInteger, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    email: Mapped[str] = mapped_column(__name_pos=Text, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(__name_pos=Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(__name_pos=DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---- Relationships ---- #
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    attempts = relationship("ExamAttempt", back_populates="user", cascade="all, delete-orphan")