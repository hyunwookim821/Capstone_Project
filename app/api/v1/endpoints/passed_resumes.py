from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.schemas.passed_resume import PassedResume, PassedResumeCreate, SimilarResume

router = APIRouter()

@router.post("/", response_model=PassedResume)
def create_passed_resume(
    *,
    db: Session = Depends(deps.get_db),
    passed_resume_in: PassedResumeCreate,
    # This should be a superuser-only endpoint in a real app
    current_user: models.User = Depends(deps.get_current_user),
) -> PassedResume:
    """
    Create a new passed resume. (For admin/data-loading purposes)
    """
    return crud.passed_resume.create_passed_resume(db=db, obj_in=passed_resume_in)

@router.get("/find_similar/{resume_id}", response_model=List[SimilarResume])
def find_similar_passed_resumes(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> List[SimilarResume]:
    """
    Find passed resumes similar to a user's resume.
    """
    user_resume = crud.resume.get(db, resume_id=resume_id)
    if not user_resume or user_resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    if not user_resume.content:
        raise HTTPException(status_code=400, detail="Resume content is empty")

    similar_resumes = crud.passed_resume.find_similar_resumes(db, resume_content=user_resume.content)
    
    # Calculate similarity scores and format the response
    results = []
    user_embedding = crud.passed_resume.model.encode(user_resume.content)
    for sr in similar_resumes:
        # Cosine similarity is 1 - (L2 distance)^2 / 2 for normalized vectors
        l2_dist = sr.embedding.l2_distance(user_embedding)
        similarity = 1 - (l2_dist ** 2) / 2
        results.append(SimilarResume(**sr.__dict__, similarity=similarity))

    return sorted(results, key=lambda x: x.similarity, reverse=True)
