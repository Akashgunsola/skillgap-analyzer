from rapidfuzz import fuzz
from app.skills.loader import load_skills

SKILL_MAP, ALIAS_MAP = load_skills()

def extract_skills(text: str):
    found = {}
    words = text.split()

    # We check n-gram phrases (1 to 3 words)
    for n in [1, 2, 3]:
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i : i + n])
            
            for alias, skill_id in ALIAS_MAP.items():
                # Only compare if the alias has the same number of words as our phrase
                if len(alias.split()) == n:
                    score = fuzz.ratio(alias, phrase)
                    if score > 90:
                        found[skill_id] = found.get(skill_id, 0) + 1
    
    return found
