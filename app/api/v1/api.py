from fastapi import APIRouter

from app.api.v1.endpoints import resumes, interviews, jobs

api_router = APIRouter()
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
