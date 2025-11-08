from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResumeBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ResumeCreate(ResumeBase):
    title: str
    content: str

class ResumeUpdate(ResumeBase):
    pass

class Resume(ResumeBase):
    resume_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
