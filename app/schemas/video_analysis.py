from pydantic import BaseModel

class VideoAnalysisBase(BaseModel):
    gaze_stability: float
    expression_stability: float
    posture_stability: float

class VideoAnalysisCreate(VideoAnalysisBase):
    interview_id: int

class VideoAnalysis(VideoAnalysisBase):
    video_analysis_id: int
    interview_id: int

    class Config:
        from_attributes = True
