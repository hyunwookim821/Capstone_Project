import os
from sqlalchemy.orm import Session
from typing import List
from sentence_transformers import SentenceTransformer

from app.models.passed_resume import PassedResume
from app.schemas.passed_resume import PassedResumeCreate

# Load the sentence transformer model from environment variable
model_name = os.getenv("EMBEDDING_MODEL", 'jhgan/ko-sroberta-multitask')
model = SentenceTransformer(model_name)

def create_passed_resume(db: Session, *, obj_in: PassedResumeCreate) -> PassedResume:
    embedding = model.encode(obj_in.content)
    db_obj = PassedResume(
        company=obj_in.company,
        job_title=obj_in.job_title,
        content=obj_in.content,
        embedding=embedding
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def find_similar_resumes(db: Session, resume_content: str, limit: int = 5) -> List[PassedResume]:
    embedding = model.encode(resume_content)
    
    # L2 distance is the default, which is fine for normalized embeddings
    similar_resumes = db.query(PassedResume).order_by(PassedResume.embedding.l2_distance(embedding)).limit(limit).all()
    return similar_resumes
