from sqlalchemy import Column, BigInteger, String, DateTime, Identity, Date, Text
from sqlalchemy.sql import func

from app.db.base import Base

class User(Base):
    user_id = Column(BigInteger, Identity(start=1), primary_key=True)
    user_name = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # New fields from My Page
    phone = Column(String(20), nullable=True)
    birthdate = Column(Date, nullable=True)
    
    desired_position = Column(String(100), nullable=True)
    desired_industry = Column(String(100), nullable=True)
    career_years = Column(String(20), nullable=True)
    career_description = Column(Text, nullable=True)

    education = Column(String(50), nullable=True)
    major = Column(String(50), nullable=True)
    skills = Column(Text, nullable=True)

    introduction = Column(Text, nullable=True)
    interview_goal = Column(Text, nullable=True)
