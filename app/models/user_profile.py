from typing import List, Optional

from pydantic import BaseModel

from app.models.skill import UserSkill


class UserSkillProfile(BaseModel):
    skills: List[UserSkill]
    embedding: Optional[List[float]] = None

