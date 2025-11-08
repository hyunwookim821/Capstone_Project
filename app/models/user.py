from sqlalchemy import Column, BigInteger, String, DateTime, Identity
from sqlalchemy.sql import func

from app.db.base import Base

class User(Base):
    user_id = Column(BigInteger, Identity(start=1), primary_key=True)
    user_name = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False) # In a real app, this should be a hashed password
    email = Column(String(50), unique=True, index=True, nullable=False)
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
