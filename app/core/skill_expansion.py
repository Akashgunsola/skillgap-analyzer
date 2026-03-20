from typing import List, Dict
from app.models.skill import UserSkill
from app.skills.neo4j_client import run_query

def get_user_expanded_skills(user_skills: List[UserSkill]) -> Dict[str, float]:
    """
    Returns a dictionary mapping skill_id to the max proficiency 
    the user has for that skill (including inherited from child skills).
    If the user has 'django' at proficiency 3, and django is a SUBSET_OF python,
    the user will be credited with 'python' at proficiency 3.
    """
    if not user_skills:
        return {}

    # Base dictionary from explicitly extracted skills
    expanded_profs = {s.skill_id: s.proficiency for s in user_skills}
    
    # Query Neo4j for all ancestors of the user's skills
    query = """
    UNWIND $user_skills AS us
    MATCH (child:Skill {skill_id: us.skill_id})-[:SUBSET_OF*1..]->(parent:Skill)
    RETURN parent.skill_id AS parent_id, us.proficiency AS proficiency
    """
    
    # Pass user_skills as a list of dicts to UNWIND
    params = {"user_skills": [{"skill_id": s.skill_id, "proficiency": s.proficiency} for s in user_skills]}
    
    try:
        results = run_query(query, parameters=params)
        for row in results:
            parent_id = row["parent_id"]
            prof = row["proficiency"]
            if parent_id in expanded_profs:
                expanded_profs[parent_id] = max(expanded_profs[parent_id], prof)
            else:
                expanded_profs[parent_id] = prof
    except Exception as e:
        print(f"Neo4j expansion failed: {e}")

    return expanded_profs
