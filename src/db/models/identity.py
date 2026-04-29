from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import BigInteger,Text
from src.db.base import Base

class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    name:Mapped[str]=mapped_column(Text)
    email:Mapped[str]=mapped_column(Text,unique=True)
    enrollments=relationship("Enrollment",back_populates="user")
    attempts=relationship("ExamAttempt",back_populates="user")