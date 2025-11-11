from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Float, Identity
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class Analysis(Base):
    __tablename__ = 'analysis'
    analysis_id = Column(BigInteger, Identity(start=1), primary_key=True)
    interview_id = Column(BigInteger, ForeignKey('interview.interview_id'), nullable=False, unique=True)
    feedback_text = Column(Text, nullable=False)
    
    # Audio analysis results
    speech_rate = Column(Float, nullable=True)
    silence_ratio = Column(Float, nullable=True)

    # Video analysis results
    gaze_stability = Column(Float, nullable=True)
    expression_stability = Column(Float, nullable=True)
    posture_stability = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview")
