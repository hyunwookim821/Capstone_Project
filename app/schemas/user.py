from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    user_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    profile_image: Optional[str] = None

class User(UserBase):
    user_id: int
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
