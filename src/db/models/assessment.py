from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import BigInteger,Numeric,DateTime,ForeignKey,Text,Index
from datetime import datetime
from src.db.base import Base

class ExamAttempt(Base):
    __tablename__="exam_attempts"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    exam_id:Mapped[int]=mapped_column(ForeignKey("exams.id"))
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    final_score:Mapped[float]=mapped_column(Numeric)
    ai_score:Mapped[float]=mapped_column(Numeric)
    human_score:Mapped[float]=mapped_column(Numeric)
    status:Mapped[str]=mapped_column(Text)
    completed_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    __table_args__=(
        Index("idx_attempt_user_id","user_id"),
        Index("idx_attempt_exam_id","exam_id"),
    )
    user=relationship("User",back_populates="attempts")
    answers=relationship("Answer",back_populates="attempt")

class Answer(Base):
    __tablename__="answers"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    attempt_id:Mapped[int]=mapped_column(ForeignKey("exam_attempts.id"))
    question_id:Mapped[int]=mapped_column(ForeignKey("questions.id"))
    option_id:Mapped[int]=mapped_column(ForeignKey("question_options.id"),nullable=True)
    student_answer:Mapped[str]=mapped_column(Text)
    score:Mapped[float]=mapped_column(Numeric)
    __table_args__=(
        Index("idx_answer_attempt_id","attempt_id"),
        Index("idx_answer_question_id","question_id"),
    )
    attempt=relationship("ExamAttempt",back_populates="answers")
    feedback=relationship("Feedback",back_populates="answer",uselist=False)

class Feedback(Base):
    __tablename__="feedback"
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    answer_id:Mapped[int]=mapped_column(ForeignKey("answers.id"))
    feedback_text:Mapped[str]=mapped_column(Text)
    reasoning:Mapped[str]=mapped_column(Text)
    __table_args__=(Index("idx_feedback_answer_id","answer_id"),)
    answer=relationship("Answer",back_populates="feedback")