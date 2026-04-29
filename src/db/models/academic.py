from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import BigInteger,Text,Integer,ForeignKey,Boolean,Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from src.db.base import Base

class Subject(Base):
    __tablename__="subjects"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    title:Mapped[str]=mapped_column(Text)
    code:Mapped[str]=mapped_column(Text)
    __table_args__=(Index("idx_subject_code","code"),)
    exams=relationship("Exam",back_populates="subject")
    enrollments=relationship("Enrollment",back_populates="subject")

class Enrollment(Base):
    __tablename__="enrollments"
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),primary_key=True)
    subject_id:Mapped[int]=mapped_column(ForeignKey("subjects.id"),primary_key=True)
    user=relationship("User",back_populates="enrollments")
    subject=relationship("Subject",back_populates="enrollments")

class Exam(Base):
    __tablename__="exams"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    subject_id:Mapped[int]=mapped_column(ForeignKey("subjects.id"))
    title:Mapped[str]=mapped_column(Text)
    time_limit:Mapped[int]=mapped_column(Integer)
    __table_args__=(Index("idx_exam_subject_id","subject_id"),)
    subject=relationship("Subject",back_populates="exams")
    questions=relationship("Question",back_populates="exam")

class Question(Base):
    __tablename__="questions"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    exam_id:Mapped[int]=mapped_column(ForeignKey("exams.id"))
    content:Mapped[str]=mapped_column(Text)
    type:Mapped[str]=mapped_column(Text)
    embedding:Mapped[list[float]]=mapped_column(Vector(1536))
    search_vector=mapped_column(TSVECTOR)
    __table_args__=(
        Index("idx_question_exam_id","exam_id"),
        Index("idx_question_search_vector","search_vector",postgresql_using="gin"),
    )
    exam=relationship("Exam",back_populates="questions")
    options=relationship("QuestionOption",back_populates="question")
    model_answer=relationship("ModelAnswer",back_populates="question",uselist=False)

class QuestionOption(Base):
    __tablename__="question_options"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    question_id:Mapped[int]=mapped_column(ForeignKey("questions.id"))
    option_text:Mapped[str]=mapped_column(Text)
    is_correct:Mapped[bool]=mapped_column(Boolean)
    __table_args__=(Index("idx_option_question_id","question_id"),)
    question=relationship("Question",back_populates="options")

class ModelAnswer(Base):
    __tablename__="model_answers"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    question_id:Mapped[int]=mapped_column(ForeignKey("questions.id"))
    content:Mapped[str]=mapped_column(Text)
    rubric:Mapped[str]=mapped_column(Text)
    embedding:Mapped[list[float]]=mapped_column(Vector(1536))
    search_vector=mapped_column(TSVECTOR)
    __table_args__=(
        Index("idx_model_answer_question_id","question_id"),
        Index("idx_model_answer_search_vector","search_vector",postgresql_using="gin"),
    )
    question=relationship("Question",back_populates="model_answer")