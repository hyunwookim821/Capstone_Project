from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class VideoAnalysis(Base):
    __tablename__ = "video_analysis"

    video_analysis_id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interview.interview_id"), unique=True, nullable=False)
    gaze_stability = Column(Float)
    expression_stability = Column(Float)
    posture_stability = Column(Float)

    interview = relationship("Interview", back_populates="video_analysis")
