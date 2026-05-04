# ---- Imports ---- #
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Integer, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from src.db.base import Base


# ---------- Models ---------- #

# ---- Subjects ---- #
class Subject(Base):
    # ---- Table Name ---- #
    __tablename__ = "subjects"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    code: Mapped[str] = mapped_column(Text)

    # ---- Indexes ---- #
    __table_args__ = (Index("idx_subject_code", "code"),)

    # ---- Relationships ---- #
    exams = relationship("Exam", back_populates="subject")
    enrollments = relationship("Enrollment", back_populates="subject")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return f"Subject(id={self.id}, title='{self.title}', code='{self.code}')"


# ---- Enrollments ---- #
class Enrollment(Base):
    # ---- Table Name ---- #
    __tablename__ = "enrollments"

    # ---- Columns ---- #
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), primary_key=True)

    # ---- Relationships ---- #
    user = relationship("User", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return f"Enrollment(user_id={self.user_id}, subject_id={self.subject_id})"


# ---- Exams ---- #
class Exam(Base):
    # ---- Table Name ---- #
    __tablename__ = "exams"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    title: Mapped[str] = mapped_column(Text)
    time_limit: Mapped[int] = mapped_column(Integer)

    # ---- Indexes ---- #
    __table_args__ = (Index("idx_exam_subject_id", "subject_id"),)

    # ---- Relationships ---- #
    subject = relationship("Subject", back_populates="exams")
    questions = relationship("Question", back_populates="exam")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Exam("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"title='{self.title}', "
            f"time_limit={self.time_limit}"
            f")"
        )


# ---- Questions ---- #
class Question(Base):
    # ---- Table Name ---- #
    __tablename__ = "questions"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))

    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_question_exam_id", "exam_id"),
        Index("idx_question_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "idx_question_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )

    # ---- Relationships ---- #
    exam = relationship("Exam", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question")
    model_answer = relationship("ModelAnswer", back_populates="question", uselist=False)

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"Question("
            f"id={self.id}, "
            f"exam_id={self.exam_id}, "
            f"type='{self.type}'"
            f")"
        )


# ---- Question Options ---- #
class QuestionOption(Base):
    # ---- Table Name ---- #
    __tablename__ = "question_options"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    option_text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_option_question_id", "question_id"),
        Index(
            "idx_option_text_trgm",
            "option_text",
            postgresql_using="gin",
            postgresql_ops={"option_text": "gin_trgm_ops"},
        ),
    )

    # ---- Relationships ---- #
    question = relationship("Question", back_populates="options")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"QuestionOption("
            f"id={self.id}, "
            f"question_id={self.question_id}, "
            f"is_correct={self.is_correct}"
            f")"
        )


# ---- Model Answers ---- #
class ModelAnswer(Base):
    # ---- Table Name ---- #
    __tablename__ = "model_answers"

    # ---- Columns ---- #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    content: Mapped[str] = mapped_column(Text)
    rubric: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))

    search_vector = mapped_column(TSVECTOR)

    # ---- Indexes ---- #
    __table_args__ = (
        Index("idx_model_answer_question_id", "question_id"),
        Index("idx_model_answer_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "idx_model_answer_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )

    # ---- Relationships ---- #
    question = relationship("Question", back_populates="model_answer")

    # ---- Repr ---- #
    def __repr__(self) -> str:
        return (
            f"ModelAnswer("
            f"id={self.id}, "
            f"question_id={self.question_id}"
            f")"
        )