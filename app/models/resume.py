from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey, Identity
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.generated_question import GeneratedQuestion # GeneratedQuestion 임포트

class Resume(Base):
    resume_id = Column(BigInteger, Identity(start=1), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    title = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    content = Column(Text, nullable=True)
    resume_file = Column(String(255), nullable=True)

    # 분석 결과를 저장할 컬럼 추가
    corrected_content = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)

    owner = relationship("User")
    # 생성된 질문과의 관계 설정
    generated_questions = relationship("GeneratedQuestion", backref="resume", order_by="GeneratedQuestion.question_id")
