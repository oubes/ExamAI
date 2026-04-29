# ---- Imports ---- #
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import BigInteger,Text,Integer,ForeignKey,Boolean,Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from src.db.base import Base


# ---------- Models ---------- #

# ---- Subjects ---- #
class Subject(Base):
    # ---- Table Name ---- #
    __tablename__="subjects"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    title:Mapped[str]=mapped_column(Text)
    code:Mapped[str]=mapped_column(Text)
    
    # ---- Indexes ---- #
    __table_args__=(Index("idx_subject_code","code"),)
    
    # ---- Relationships ---- #
    exams=relationship("Exam",back_populates="subject")
    enrollments=relationship("Enrollment",back_populates="subject")

# ---- Enrollments ---- #
class Enrollment(Base):
    # ---- Table Name ---- #
    __tablename__="enrollments"
    
    # ---- Columns ---- #
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),primary_key=True)
    subject_id:Mapped[int]=mapped_column(ForeignKey("subjects.id"),primary_key=True)
    
    # ---- Relationships ---- #
    user=relationship("User",back_populates="enrollments")
    subject=relationship("Subject",back_populates="enrollments")

# ---- Exams ---- #
class Exam(Base):
    # ---- Table Name ---- #
    __tablename__="exams"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    subject_id:Mapped[int]=mapped_column(ForeignKey("subjects.id"))
    title:Mapped[str]=mapped_column(Text)
    time_limit:Mapped[int]=mapped_column(Integer)
    
    # ---- Indexes ---- #
    __table_args__=(Index("idx_exam_subject_id","subject_id"),)
    
    # ---- Relationships ---- #
    subject=relationship("Subject",back_populates="exams")
    questions=relationship("Question",back_populates="exam")

# ---- Questions ---- #
class Question(Base):
    # ---- Table Name ---- #
    __tablename__="questions"
    
    # ---- Columns ---- #
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    exam_id:Mapped[int]=mapped_column(ForeignKey("exams.id"))
    content:Mapped[str]=mapped_column(Text)
    type:Mapped[str]=mapped_column(Text)
    embedding:Mapped[list[float]]=mapped_column(Vector(1024))
    
    # ---- Indexes ---- #
    search_vector=mapped_column(TSVECTOR)
    __table_args__=(
        Index("idx_question_exam_id","exam_id"),
        Index("idx_question_search_vector","search_vector",postgresql_using="gin"),
    )
    
    # ---- Relationships ---- #
    exam=relationship("Exam",back_populates="questions")
    options=relationship("QuestionOption",back_populates="question")
    model_answer=relationship("ModelAnswer",back_populates="question",uselist=False)

# ---- Question Options ---- #
class QuestionOption(Base):
    # ---- Table Name ---- #
    __tablename__="question_options"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    question_id:Mapped[int]=mapped_column(ForeignKey("questions.id"))
    option_text:Mapped[str]=mapped_column(Text)
    is_correct:Mapped[bool]=mapped_column(Boolean)
    
    # ---- Indexes ---- #
    __table_args__=(Index("idx_option_question_id","question_id"),)
    
    # ---- Relationships ---- #
    question=relationship("Question",back_populates="options")

# ---- Model Answers ---- #
class ModelAnswer(Base):
    # ---- Table Name ---- #
    __tablename__="model_answers"
    
    # ---- Columns ---- #
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    question_id:Mapped[int]=mapped_column(ForeignKey("questions.id"))
    content:Mapped[str]=mapped_column(Text)
    rubric:Mapped[str]=mapped_column(Text)
    embedding:Mapped[list[float]]=mapped_column(Vector(1024))
    
    #  ---- Indexes ---- #
    search_vector=mapped_column(TSVECTOR)
    __table_args__=(
        Index("idx_model_answer_question_id","question_id"),
        Index("idx_model_answer_search_vector","search_vector",postgresql_using="gin"),
    )
    
    # ---- Relationships ---- #
    question=relationship("Question",back_populates="model_answer")