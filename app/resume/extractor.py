from rapidfuzz import fuzz
from app.skills.loader import load_skills

SKILL_MAP, ALIAS_MAP = load_skills()

def extract_skills(text: str):
    found = {}

    words = text.split()

    for i in range(len(words)):
        phrase = " ".join(words[i:i+3])

        for alias, skill_id in ALIAS_MAP.items():
            score = fuzz.partial_ratio(alias, phrase)
            if score > 85:
                found[skill_id] = found.get(skill_id, 0) + 1

    return found
