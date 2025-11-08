from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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

class AnswerCreate(AnswerBase):
    question_id: int

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