from pydantic import BaseModel

class GrammarCheckResult(BaseModel):
    original: str
    corrected: str