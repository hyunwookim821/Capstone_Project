from sqlalchemy.orm import Session
from typing import List

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate


def get(db: Session, resume_id: int):
    return db.query(Resume).filter(Resume.resume_id == resume_id).first()

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

def update(db: Session, *, db_obj: Resume, obj_in: ResumeUpdate) -> Resume:
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, resume_id: int) -> Resume:
    obj = db.query(Resume).get(resume_id)
    db.delete(obj)
    db.commit()
    return obj
