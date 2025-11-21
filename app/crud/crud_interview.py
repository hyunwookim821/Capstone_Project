from sqlalchemy.orm import Session
from typing import List

from app.models.interview import Interview, Question, Answer
from app.schemas.interview import InterviewCreate, QuestionCreate, AnswerCreate

# CRUD for Interview
def get_interview(db: Session, interview_id: int) -> Interview | None:
    return db.query(Interview).filter(Interview.interview_id == interview_id).first()

def create_interview(db: Session, *, obj_in: InterviewCreate) -> Interview:
    db_obj = Interview(
        user_id=obj_in.user_id,
        resume_id=obj_in.resume_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# CRUD for Question
def create_question(db: Session, *, obj_in: QuestionCreate) -> Question:
    db_obj = Question(
        interview_id=obj_in.interview_id,
        question_text=obj_in.question_text
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_questions_by_interview(db: Session, interview_id: int) -> List[Question]:
    return db.query(Question).filter(Question.interview_id == interview_id).order_by(Question.question_id).all()

def get_latest_questions_by_resume(db: Session, resume_id: int) -> List[Question]:
    """
    Finds the most recent interview for a given resume and returns its questions.
    """
    latest_interview = db.query(Interview).filter(Interview.resume_id == resume_id).order_by(Interview.created_at.desc()).first()
    if not latest_interview:
        return []
    return db.query(Question).filter(Question.interview_id == latest_interview.interview_id).order_by(Question.question_id).all()


# CRUD for Answer
def create_answer(db: Session, *, obj_in: AnswerCreate) -> Answer:
    db_obj = Answer(
        question_id=obj_in.question_id,
        answer_text=obj_in.answer_text,
        audio_path=obj_in.audio_path,
        whisper_result=obj_in.whisper_result  # Whisper 결과 저장
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_answers_by_interview(db: Session, interview_id: int) -> List[Answer]:
    """
    특정 면접의 모든 답변을 조회합니다.
    """
    return (
        db.query(Answer)
        .join(Question, Answer.question_id == Question.question_id)
        .filter(Question.interview_id == interview_id)
        .all()
    )
