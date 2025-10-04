from pydantic import BaseModel
from typing import List

class GrammarError(BaseModel):
    original: str
    corrected: str
    context: str
    type: str

class GrammarAnalysis(BaseModel):
    errors: List[GrammarError]
    error_count: int
