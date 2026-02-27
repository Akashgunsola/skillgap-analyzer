from pydantic import BaseModel

class UserSkill(BaseModel):
    skill_id: str
    name: str
    proficiency: int
    evidence_count: int
