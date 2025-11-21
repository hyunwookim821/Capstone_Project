"""
프롬프트 모듈
LLM에 전달하는 프롬프트들을 중앙 관리합니다.
"""

from .interview_prompts import (
    get_question_generation_prompt,
    get_interview_analysis_prompt,
)
from .resume_prompts import (
    get_resume_feedback_prompt,
)

__all__ = [
    "get_question_generation_prompt",
    "get_interview_analysis_prompt",
    "get_resume_feedback_prompt",
]