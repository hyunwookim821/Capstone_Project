from sqlalchemy.orm import Session
from app.models.generated_question import GeneratedQuestion
from app.schemas.generated_question import GeneratedQuestionCreate

def create_question(db: Session, obj_in: GeneratedQuestionCreate) -> GeneratedQuestion:
    db_obj = GeneratedQuestion(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_questions_by_resume(db: Session, resume_id: int) -> list[GeneratedQuestion]:
    return db.query(GeneratedQuestion).filter(GeneratedQuestion.resume_id == resume_id).all()
