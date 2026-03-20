import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.skill_expansion import get_user_expanded_skills
from app.models.skill import UserSkill

def main():
    skills = [
        UserSkill(skill_id="django", name="Django", proficiency=3, evidence_count=1)
    ]
    expanded = get_user_expanded_skills(skills)
    print("Original Skills:", [{"id": s.skill_id, "prof": s.proficiency} for s in skills])
    print("Expanded Skills:", expanded)

if __name__ == "__main__":
    main()
