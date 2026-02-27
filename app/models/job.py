from pydantic import BaseModel
from typing import List

class JobRequirement(BaseModel):
    skill_id: str
    weight: float
    required_level: int = 3

class Job(BaseModel):
    title: str
    extracted_skills: List[JobRequirement]
