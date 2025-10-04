from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class InterviewBase(BaseModel):
    status: Optional[str] = 'scheduled'
    resume_id: Optional[int] = None
    job_id: Optional[int] = None

class InterviewCreate(InterviewBase):
    resume_id: int

class InterviewUpdate(InterviewBase):
    pass

class Interview(InterviewBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
