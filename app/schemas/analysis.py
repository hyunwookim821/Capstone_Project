from pydantic import BaseModel

class GrammarAnalysis(BaseModel):
    error_count: int
    corrected_sentence: str