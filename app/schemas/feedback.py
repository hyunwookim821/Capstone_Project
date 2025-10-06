from pydantic import BaseModel

class AIFeedback(BaseModel):
    feedback: str
