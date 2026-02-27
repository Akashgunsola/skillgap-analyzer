from typing import List, Optional

from pydantic import BaseModel

from app.models.job import Job
from app.models.user_profile import UserSkillProfile


class ResumeUploadResponse(BaseModel):
    profile: UserSkillProfile


class JobInput(BaseModel):
    title: str
    description: str


class JobListRequest(BaseModel):
    jobs: List[JobInput]


class JobListResponse(BaseModel):
    jobs: List[Job]


class FitScorePerJob(BaseModel):
    job: Job
    fit_score: float
    category: str


class GapItem(BaseModel):
    skill_id: str
    name: str
    weight: float
    difficulty: int
    learning_hours: int
    gap_score: float


class RoadmapItem(BaseModel):
    timeframe: str
    learning_focus: str
    learning_hours: int
    priority_score: float


class AnalysisRequest(BaseModel):
    profile: UserSkillProfile
    jobs: List[Job]
    weekly_hours: Optional[int] = None


class AnalysisResponse(BaseModel):
    fit_results: List[FitScorePerJob]
    gaps: List[GapItem]
    roadmap: List[RoadmapItem]

