import os
import sys

# Add the project root to the PATH to allow ffmpeg to be found.
# This is a workaround for deployment so system-wide changes aren't needed.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# In Windows, os.environ["PATH"] is separated by semicolons
os.environ["PATH"] = f"{project_root};{os.environ['PATH']}"

from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(title="JobPrep API")


@app.get("/")
def read_root():
    return {"message": "Welcome to the JobPrep API"}


app.include_router(api_router, prefix="/api/v1")
