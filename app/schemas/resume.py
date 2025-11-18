from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.schemas.generated_question import GeneratedQuestion # GeneratedQuestion 임포트

class ResumeBase(BaseModel):
    title: str
    content: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    corrected_content: Optional[str] = None
    ai_feedback: Optional[str] = None

class Resume(ResumeBase):
    resume_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResumeDetail(Resume):
    corrected_content: Optional[str] = None
    ai_feedback: Optional[str] = None
    generated_questions: List[GeneratedQuestion] = Field(default_factory=list)

    class Config:
        from_attributes = True
