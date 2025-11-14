from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date # Import date for birthdate

class UserBase(BaseModel):
    user_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel): # Inherit from BaseModel directly for more flexibility
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[date] = None # Use date type
    desired_position: Optional[str] = None
    desired_industry: Optional[str] = None
    career_years: Optional[str] = None
    career_description: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    skills: Optional[str] = None
    introduction: Optional[str] = None
    interview_goal: Optional[str] = None

class User(UserBase):
    user_id: int
    profile_image: Optional[str] = None
    created_at: datetime
    phone: Optional[str] = None
    birthdate: Optional[date] = None
    desired_position: Optional[str] = None
    desired_industry: Optional[str] = None
    career_years: Optional[str] = None
    career_description: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    skills: Optional[str] = None
    introduction: Optional[str] = None
    interview_goal: Optional[str] = None

    class Config:
        from_attributes = True
