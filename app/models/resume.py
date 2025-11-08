from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey, Identity
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Resume(Base):
    resume_id = Column(BigInteger, Identity(start=1), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    title = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    content = Column(Text, nullable=True)
    resume_file = Column(String(255), nullable=True)

    owner = relationship("User")
