from pydantic import BaseModel

class AIFeedback(BaseModel):
    error_count: int
    corrected_sentence: str
    feedback: str
