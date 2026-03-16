from typing import List, Dict
from app.models.skill import UserSkill
from app.models.job import Job
from app.skills.neo4j_client import run_query
from app.skills.loader import load_skills

def analyze_gaps(user_skills: List[UserSkill], job: Job) -> List[Dict]:
    """
    Identifies missing skills for a given job and ranks them by learning ROI (Gap Score)
    using Neo4j Graph queries.
    """
    user_skill_ids = [s.skill_id for s in user_skills]
    
    query = """
    MATCH (j:JobRole {title: $target_role})-[r:REQUIRES_SKILL]->(s:Skill)
    RETURN s.name AS skill_name, s.skill_id AS skill_id, r.weight AS weight, 
           s.difficulty AS difficulty, s.learning_hours AS learning_hours
    """
    
    records = []
    try:
        records = run_query(query, parameters={"target_role": job.title})
    except Exception as e:
        print(f"Neo4j query failed: {e}")

    gaps = []
    
    # 1. Neo4j-based Gap Analysis
    if records:
        for req in records:
            if req["skill_id"] not in user_skill_ids:
                # We could add semantic matching checks via EXPECTED RELATED_TO cypher here 
                difficulty = req.get("difficulty") or 2
                learning_hours = req.get("learning_hours") or 40
                
                if learning_hours == 0:
                    learning_hours = 1
                    
                gap_score = (req["weight"] * difficulty) / learning_hours
                
                gaps.append({
                    "skill_id": req["skill_id"],
                    "name": req["skill_name"],
                    "weight": req["weight"],
                    "difficulty": difficulty,
                    "learning_hours": learning_hours,
                    "gap_score": gap_score,
                    "type": "Missing"
                })

    # 2. Fallback to basic JSON extraction if NLP job parser sent standalone skills without matching Neo4j ontology
    else:
        skill_map, _ = load_skills()
        for req in job.extracted_skills:
            if req.skill_id not in user_skill_ids:
                skill_meta = skill_map.get(req.skill_id)
                if not skill_meta:
                    continue
                    
                difficulty = skill_meta.get("difficulty", 2)
                learning_hours = skill_meta.get("learning_hours", 40)
                if learning_hours == 0:
                    learning_hours = 1
                    
                gap_score = (req.weight * difficulty) / learning_hours
                
                gaps.append({
                    "skill_id": req.skill_id,
                    "name": skill_meta.get("name", req.skill_id),
                    "weight": req.weight,
                    "difficulty": difficulty,
                    "learning_hours": learning_hours,
                    "gap_score": gap_score,
                    "type": "Missing"
                })
                
    # Sort DESCENDING by gap_score (highest ROI first)
    gaps.sort(key=lambda x: x["gap_score"], reverse=True)
    
    return gaps
