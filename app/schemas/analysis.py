from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnalysisBase(BaseModel):
    feedback_text: str
    speech_rate: Optional[float] = None
    silence_ratio: Optional[float] = None
    gaze_stability: Optional[float] = None
    expression_stability: Optional[float] = None
    posture_stability: Optional[float] = None

class AnalysisCreate(AnalysisBase):
    interview_id: int

class AnalysisUpdate(AnalysisBase):
    pass

class Analysis(AnalysisBase):
    analysis_id: int
    interview_id: int
    resume_id: Optional[int] = None  # 재면접을 위한 resume_id 추가
    created_at: datetime

    class Config:
        from_attributes = True

class GrammarAnalysis(BaseModel):
    error_count: int
    corrected_sentence: str