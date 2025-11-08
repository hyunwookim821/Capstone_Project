from fastapi import APIRouter

from app.api.v1.endpoints import users, resumes, interviews, login, passed_resumes

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(passed_resumes.router, prefix="/passed-resumes", tags=["passed-resumes"])
