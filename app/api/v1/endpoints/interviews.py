from fastapi import APIRouter, HTTPException
from typing import List, Any
from datetime import datetime

from app.schemas.interview import Interview, InterviewCreate, InterviewUpdate

router = APIRouter()

# Dummy database
DUMMY_INTERVIEWS = {
    1: {
        "id": 1,
        "owner_id": 1,
        "resume_id": 1,
        "job_id": 1,
        "status": "completed",
        "created_at": datetime(2023, 1, 10),
        "updated_at": datetime(2023, 1, 11),
    },
}

@router.get("/", response_model=List[Interview])
def read_interviews(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve interviews.
    """
    return list(DUMMY_INTERVIEWS.values())[skip:limit]

@router.post("/", response_model=Interview)
def create_interview(
    *,
    interview_in: InterviewCreate,
) -> Any:
    """
    Create new interview session.
    """
    new_id = max(DUMMY_INTERVIEWS.keys()) + 1
    interview = Interview(
        id=new_id,
        owner_id=1,  # Assuming a default owner
        resume_id=interview_in.resume_id,
        job_id=interview_in.job_id,
        status='scheduled',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    DUMMY_INTERVIEWS[new_id] = interview.dict()
    return interview

@router.get("/{interview_id}", response_model=Interview)
def read_interview(
    *,
    interview_id: int,
) -> Any:
    """
    Get interview by ID.
    """
    if interview_id not in DUMMY_INTERVIEWS:
        raise HTTPException(status_code=404, detail="Interview not found")
    return DUMMY_INTERVIEWS[interview_id]

@router.put("/{interview_id}", response_model=Interview)
def update_interview(
    *,
    interview_id: int,
    interview_in: InterviewUpdate,
) -> Any:
    """
    Update an interview.
    """
    if interview_id not in DUMMY_INTERVIEWS:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview = DUMMY_INTERVIEWS[interview_id]
    update_data = interview_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        interview[field] = value
    interview["updated_at"] = datetime.now()

    DUMMY_INTERVIEWS[interview_id] = interview
    return interview

@router.delete("/{interview_id}", response_model=Interview)
def delete_interview(
    *,
    interview_id: int,
) -> Any:
    """
    Delete an interview.
    """
    if interview_id not in DUMMY_INTERVIEWS:
        raise HTTPException(status_code=404, detail="Interview not found")

    deleted_interview = DUMMY_INTERVIEWS.pop(interview_id)
    return deleted_interview
