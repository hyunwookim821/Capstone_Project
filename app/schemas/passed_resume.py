from pydantic import BaseModel
from typing import Optional

class PassedResumeBase(BaseModel):
    company: str
    job_title: str
    content: str

class PassedResumeCreate(PassedResumeBase):
    pass

class PassedResume(PassedResumeBase):
    id: int

    class Config:
        from_attributes = True

class SimilarResume(PassedResume):
    similarity: float
