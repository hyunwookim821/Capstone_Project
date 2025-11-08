from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, Identity
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Analysis(Base):
    __tablename__ = "analysis"

    analysis_id = Column(BigInteger, Identity(start=1), primary_key=True)
    interview_id = Column(BigInteger, ForeignKey("interview.interview_id"))
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    interview = relationship("Interview")
