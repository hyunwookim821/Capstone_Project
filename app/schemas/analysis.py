from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnalysisBase(BaseModel):
    feedback_text: Optional[str] = None

class AnalysisCreate(AnalysisBase):
    interview_id: int
    feedback_text: str

class Analysis(AnalysisBase):
    analysis_id: int
    interview_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GrammarAnalysis(BaseModel):
    error_count: int
    corrected_sentence: str