from sqlalchemy.orm import Session, joinedload
from typing import List, Any, Dict, Optional, Union

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate
from app import models # models 임포트 추가

def get(db: Session, resume_id: int) -> Optional[Resume]:
    return db.query(Resume).options(joinedload(models.Resume.generated_questions)).filter(Resume.resume_id == resume_id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Resume]:
    return db.query(Resume).offset(skip).limit(limit).all()

def get_multi_by_owner(
    db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
) -> List[Resume]:
    return (
        db.query(Resume)
        .filter(Resume.user_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create(db: Session, *, obj_in: ResumeCreate, user_id: int) -> Resume:
    db_obj = Resume(
        title=obj_in.title,
        content=obj_in.content,
        user_id=user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, *, db_obj: Resume, obj_in: Union[ResumeUpdate, Dict[str, Any]]) -> Resume:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, resume_id: int) -> Optional[Resume]:
    # Eagerly load related entities
    obj = db.query(Resume).options(
        joinedload(Resume.generated_questions)
    ).filter(Resume.resume_id == resume_id).first()

    if not obj:
        return None  # Or raise an exception

    # Delete dependent generated questions
    for question in obj.generated_questions:
        db.delete(question)

    # Find and delete dependent interviews
    interviews = db.query(models.Interview).filter(models.Interview.resume_id == resume_id).all()
    for interview in interviews:
        db.delete(interview)

    # Now delete the resume itself
    db.delete(obj)
    db.commit()
    return obj
