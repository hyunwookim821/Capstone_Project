from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate

def create_analysis(db: Session, *, obj_in: AnalysisCreate) -> Analysis:
    db_obj = Analysis(
        interview_id=obj_in.interview_id,
        feedback_text=obj_in.feedback_text,
        speech_rate=obj_in.speech_rate,
        silence_ratio=obj_in.silence_ratio
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_analysis_by_interview(db: Session, interview_id: int) -> Analysis | None:
    return db.query(Analysis).filter(Analysis.interview_id == interview_id).first()

def update_analysis(db: Session, *, db_obj: Analysis, obj_in: Dict[str, Any]) -> Analysis:
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

