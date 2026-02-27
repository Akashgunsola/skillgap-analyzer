from typing import List

from pydantic import BaseModel

from app.models.skill import UserSkill


class UserSkillProfile(BaseModel):
    skills: List[UserSkill]

