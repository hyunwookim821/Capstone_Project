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
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
