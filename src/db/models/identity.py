# ---- Imports ---- #
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import BigInteger,Text
from db.base import Base


# ---------- Models ---------- #

# ---- User ---- #
class User(Base):
    # ---- Table Name ---- #
    __tablename__="users"

    # ---- Columns ---- #
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    name:Mapped[str]=mapped_column(Text)
    email:Mapped[str]=mapped_column(Text,unique=True)

    # ---- Relationships ---- #
    enrollments=relationship("Enrollment",back_populates="user")
    attempts=relationship("ExamAttempt",back_populates="user")