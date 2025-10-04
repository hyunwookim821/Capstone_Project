from fastapi import APIRouter, HTTPException
from typing import List, Any
from datetime import datetime

from app.schemas.job import Job, JobCreate, JobUpdate

router = APIRouter()

# Dummy database
DUMMY_JOBS = {
    1: {
        "id": 1,
        "title": "Software Engineer",
        "company": "Google",
        "description": "Build the future of search.",
        "requirements": "BS in Computer Science, 5+ years of experience.",
        "created_at": datetime(2023, 1, 5),
        "updated_at": datetime(2023, 1, 5),
    },
}

@router.get("/", response_model=List[Job])
def read_jobs(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve jobs.
    """
    return list(DUMMY_JOBS.values())[skip:limit]

@router.post("/", response_model=Job)
def create_job(
    *,
    job_in: JobCreate,
) -> Any:
    """
    Create new job.
    """
    new_id = max(DUMMY_JOBS.keys()) + 1
    job = Job(
        id=new_id,
        title=job_in.title,
        company=job_in.company,
        description=job_in.description,
        requirements=job_in.requirements or "",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    DUMMY_JOBS[new_id] = job.dict()
    return job

@router.get("/{job_id}", response_model=Job)
def read_job(
    *,
    job_id: int,
) -> Any:
    """
    Get job by ID.
    """
    if job_id not in DUMMY_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return DUMMY_JOBS[job_id]

@router.put("/{job_id}", response_model=Job)
def update_job(
    *,
    job_id: int,
    job_in: JobUpdate,
) -> Any:
    """
    Update a job.
    """
    if job_id not in DUMMY_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")

    job = DUMMY_JOBS[job_id]
    update_data = job_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        job[field] = value
    job["updated_at"] = datetime.now()

    DUMMY_JOBS[job_id] = job
    return job

@router.delete("/{job_id}", response_model=Job)
def delete_job(
    *,
    job_id: int,
) -> Any:
    """
    Delete a job.
    """
    if job_id not in DUMMY_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")

    deleted_job = DUMMY_JOBS.pop(job_id)
    return deleted_job
