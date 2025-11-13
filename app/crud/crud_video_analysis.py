from sqlalchemy.orm import Session
from app.models.video_analysis import VideoAnalysis
from app.schemas.video_analysis import VideoAnalysisCreate

def create(db: Session, *, obj_in: VideoAnalysisCreate) -> VideoAnalysis:
    db_obj = VideoAnalysis(
        interview_id=obj_in.interview_id,
        gaze_stability=obj_in.gaze_stability,
        expression_stability=obj_in.expression_stability,
        posture_stability=obj_in.posture_stability,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_by_interview_id(db: Session, interview_id: int):
    return db.query(VideoAnalysis).filter(VideoAnalysis.interview_id == interview_id).first()