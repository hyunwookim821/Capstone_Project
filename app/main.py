from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(title="JobPrep API")


@app.get("/")
def read_root():
    return {"message": "Welcome to the JobPrep API"}


app.include_router(api_router, prefix="/api/v1")
