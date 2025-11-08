from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey, Identity
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Interview(Base):
    __tablename__ = "interview"

    interview_id = Column(BigInteger, Identity(start=1), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    resume_id = Column(BigInteger, ForeignKey("resume.resume_id"))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    resume = relationship("Resume")
    questions = relationship("Question", back_populates="interview")


class Question(Base):
    __tablename__ = "question"

    question_id = Column(BigInteger, Identity(start=1), primary_key=True)
    interview_id = Column(BigInteger, ForeignKey("interview.interview_id"))
    question_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    interview = relationship("Interview", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "answer"

    answer_id = Column(BigInteger, Identity(start=1), primary_key=True)
    question_id = Column(BigInteger, ForeignKey("question.question_id"))
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    question = relationship("Question", back_populates="answers")
