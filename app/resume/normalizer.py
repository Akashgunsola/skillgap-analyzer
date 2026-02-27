from app.skills.loader import load_skills

SKILL_MAP, _ = load_skills()

def normalize_skills(raw_skills: dict):
    normalized = []

    for skill_id, freq in raw_skills.items():
        skill = SKILL_MAP[skill_id]
        normalized.append({
            "skill_id": skill_id,
            "name": skill["name"],
            "frequency": freq
        })

    return normalized
