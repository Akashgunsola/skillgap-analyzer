"""
Seed Neo4j with Skill nodes and SUBSET_OF edges from app/skills/ontology.json.
Run from repo root: python -m app.ontology.seed_from_json
"""

import json
import sys
from pathlib import Path

# Ensure app is on path when run as __main__
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.skills.neo4j_client import run_query


def load_ontology_json() -> list:
    path = Path(__file__).resolve().parents[1] / "skills" / "ontology.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_skills(skills: list) -> None:
    for skill in skills:
        run_query(
            """
            MERGE (s:Skill {skill_id: $skill_id})
            ON CREATE SET
                s.name = $name,
                s.aliases = $aliases,
                s.difficulty = $difficulty,
                s.learning_hours = $learning_hours,
                s.category = $category
            ON MATCH SET
                s.name = $name,
                s.aliases = $aliases,
                s.difficulty = $difficulty,
                s.learning_hours = $learning_hours,
                s.category = $category
            """,
            {
                "skill_id": skill["skill_id"],
                "name": skill["name"],
                "aliases": skill.get("aliases") or [],
                "difficulty": skill.get("difficulty", 2),
                "learning_hours": skill.get("learning_hours", 40),
                "category": skill.get("category") or "skill",
            },
        )


def seed_subset_edges(skills: list) -> None:
    for skill in skills:
        parent_id = skill.get("parent")
        if not parent_id:
            continue
        run_query(
            """
            MATCH (child:Skill {skill_id: $child_id}), (parent:Skill {skill_id: $parent_id})
            MERGE (child)-[:SUBSET_OF]->(parent)
            """,
            {"child_id": skill["skill_id"], "parent_id": parent_id},
        )


def main() -> None:
    skills = load_ontology_json()
    if not skills:
        print("No skills in ontology.json")
        return
    seed_skills(skills)
    seed_subset_edges(skills)
    print(f"Seeded {len(skills)} skills and SUBSET_OF edges into Neo4j.")


if __name__ == "__main__":
    main()
