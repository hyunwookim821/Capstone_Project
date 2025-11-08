from sqlalchemy import Column, BigInteger, String, Text, Identity
from pgvector.sqlalchemy import Vector

from app.db.base import Base

class PassedResume(Base):
    __tablename__ = "passed_resume"

    id = Column(BigInteger, Identity(start=1), primary_key=True)
    company = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
