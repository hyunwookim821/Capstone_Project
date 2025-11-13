import os
import sys

# Add the project root to the PATH to allow ffmpeg to be found.
# This is a workaround for deployment so system-wide changes aren't needed.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# In Windows, os.environ["PATH"] is separated by semicolons
os.environ["PATH"] = f"{project_root};{os.environ['PATH']}"

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.db.session import SessionLocal
from app.models.user import User

app = FastAPI(title="JobPrep API")

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    # Create a dummy user for testing if not exists
    user = db.query(User).filter(User.user_id == 1).first()
    if not user:
        dummy_user = User(
            user_id=1,
            user_name="testuser",
            email="test@example.com",
            password="testpassword"
        )
        db.add(dummy_user)
        db.commit()
    db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to the JobPrep API"}


app.include_router(api_router, prefix="/api/v1")

# Add diagnostic code to print all registered routes
from fastapi.routing import APIRoute

print("--- Registered API Routes ---")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")
print("-----------------------------")

