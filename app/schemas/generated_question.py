from pydantic import BaseModel

class GeneratedQuestionBase(BaseModel):
    resume_id: int
    question_text: str

class GeneratedQuestionCreate(GeneratedQuestionBase):
    pass

class GeneratedQuestion(GeneratedQuestionBase):
    question_id: int

    class Config:
        from_attributes = True
