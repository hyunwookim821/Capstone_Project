from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Identity
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.base import Base
from app.models.user import User  # Import User model


class Interview(Base):
    __tablename__ = 'interview'
    interview_id = Column(BigInteger, Identity(start=1), primary_key=True)
    user_id = Column(BigInteger, ForeignKey(User.user_id), nullable=False)  # Direct reference
    resume_id = Column(BigInteger, ForeignKey('resume.resume_id'), nullable=False)
    video_path = Column(String(255), nullable=True)  # Path to the video file
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    resume = relationship("Resume")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "question"

    question_id = Column(BigInteger, Identity(start=1), primary_key=True)
    interview_id = Column(BigInteger, ForeignKey("interview.interview_id"))
    question_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    interview = relationship("Interview", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = 'answer'
    answer_id = Column(BigInteger, Identity(start=1), primary_key=True)
    question_id = Column(BigInteger, ForeignKey('question.question_id'), nullable=False)
    answer_text = Column(Text, nullable=False)
    audio_path = Column(String(255), nullable=True)  # Path to the audio file
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="answers")
