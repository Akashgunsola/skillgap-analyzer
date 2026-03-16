import sys
import os
import itertools
from dotenv import load_dotenv

# Add project root to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.skills.neo4j_client import session
from app.skills.loader import load_skills
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]

def seed_database():
    print("Loading skill ontology...")
    skill_map, alias_map = load_skills()

    print("Loading Sentence Transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Process skills and embeddings
    skills_data = []
    print("Computing embeddings for skills...")
    for skill_id, skill_info in skill_map.items():
        embedding = model.encode(skill_info["name"])
        skills_data.append({
            **skill_info,
            "embedding": embedding
        })

    with session() as s:
        print("Clearing database...")
        s.run("MATCH (n) DETACH DELETE n;")

        print("Seeding Skill nodes...")
        for skill in skills_data:
            s.run("""
                MERGE (sk:Skill {name: $name, skill_id: $skill_id})
                SET sk.category = $category,
                    sk.difficulty = $difficulty,
                    sk.learning_hours = $learning_hours,
                    sk.aliases = $aliases
            """, **skill)

        print("Creating parent-child (SUBSET_OF) relationships...")
        for skill in skills_data:
            if skill.get("parent"):
                s.run("""
                    MATCH (child:Skill {skill_id: $child_id}), (parent:Skill {skill_id: $parent_id})
                    MERGE (child)-[:SUBSET_OF]->(parent)
                """, child_id=skill["skill_id"], parent_id=skill["parent"])

        print("Creating RELATED_TO relationships based on semantic similarity...")
        for s1, s2 in itertools.combinations(skills_data, 2):
            sim = calculate_cosine_similarity(s1["embedding"], s2["embedding"])
            if float(sim) > 0.6:  # Threshold for relating skills
                s.run("""
                    MATCH (sk1:Skill {skill_id: $s1_id}), (sk2:Skill {skill_id: $s2_id})
                    MERGE (sk1)-[:RELATED_TO {similarity: $sim}]->(sk2)
                    MERGE (sk2)-[:RELATED_TO {similarity: $sim}]->(sk1)
                """, s1_id=s1["skill_id"], s2_id=s2["skill_id"], sim=float(sim))

        print("Seeding sample Job Roles...")
        # Hardcoding a few jobs based on current small ontology
        jobs = [
            {
                "title": "Backend Web Developer",
                "skills": [
                    {"id": "python", "weight": 0.9, "must_have": True},
                    {"id": "django", "weight": 0.8, "must_have": False},
                    {"id": "sql", "weight": 0.7, "must_have": True}
                ]
            },
            {
                "title": "Data Analyst",
                "skills": [
                    {"id": "python", "weight": 0.8, "must_have": True},
                    {"id": "sql", "weight": 0.9, "must_have": True}
                ]
            }
        ]

        for job in jobs:
            s.run("MERGE (j:JobRole {title: $title})", title=job["title"])
            for req in job["skills"]:
                s.run("""
                    MATCH (j:JobRole {title: $title}), (sk:Skill {skill_id: $skill_id})
                    MERGE (j)-[r:REQUIRES_SKILL]->(sk)
                    SET r.weight = $weight, r.is_must_have = $must_have
                """, title=job["title"], skill_id=req["id"], weight=req["weight"], must_have=req["must_have"])

        print("Seeding complete.")

if __name__ == "__main__":
    load_dotenv(override=True)
    seed_database()
