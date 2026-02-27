import json
from pathlib import Path

def load_skills():
    path = Path(__file__).parent / "ontology.json"
    with open(path, "r", encoding="utf-8") as f:
        skills = json.load(f)

    skill_map = {}
    alias_map = {}

    for skill in skills:
        skill_map[skill["skill_id"]] = skill
        alias_map[skill["name"].lower()] = skill["skill_id"]

        for alias in skill["aliases"]:
            alias_map[alias.lower()] = skill["skill_id"]

    return skill_map, alias_map
