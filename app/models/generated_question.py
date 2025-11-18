from sqlalchemy import Column, BigInteger, Text, ForeignKey, Identity
from app.db.base import Base

class GeneratedQuestion(Base):
    __tablename__ = "generated_question"

    question_id = Column(BigInteger, Identity(start=1), primary_key=True)
    resume_id = Column(BigInteger, ForeignKey("resume.resume_id"), nullable=False)
    question_text = Column(Text, nullable=False)
