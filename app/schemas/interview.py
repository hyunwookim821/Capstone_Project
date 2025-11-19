from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

# Schema for Question
class QuestionBase(BaseModel):
    question_text: str

class QuestionCreate(QuestionBase):
    interview_id: int

class Question(QuestionBase):
    question_id: int
    interview_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for Answer
class AnswerBase(BaseModel):
    answer_text: str
    audio_path: Optional[str] = None

class AnswerCreate(AnswerBase):
    question_id: int
    whisper_result: Optional[Dict[str, Any]] = None

class AnswerUpdate(AnswerBase):
    pass

class Answer(AnswerBase):
    answer_id: int
    question_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for Interview
class InterviewBase(BaseModel):
    user_id: int
    resume_id: int
    video_path: Optional[str] = None

class InterviewCreate(InterviewBase):
    pass

class Interview(InterviewBase):
    interview_id: int
    created_at: datetime
    questions: List[Question] = []

    class Config:
        from_attributes = True

class InterviewSession(BaseModel):
    interview_id: int
    questions: List[str]

class QuestionList(BaseModel):
    questions: List[str]

class VideoAnalysisRequest(BaseModel):
    landmarks: List[Dict[str, Any]]