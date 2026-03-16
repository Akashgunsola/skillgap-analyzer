from typing import List, Tuple, Dict, Any, Optional
from app.models.skill import UserSkill
from app.models.job import Job
from app.skills.neo4j_client import run_query
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_fit_score(user_skills: List[UserSkill], job: Job) -> Tuple[float, str]:
    """
    Calculates the fit score between a user's skills and a job's requirements.
    (Legacy calculation for specific job objects passed into the API)
    """
    if not job.extracted_skills:
        return 0.0, "Low Probability"

    user_skill_dict = {s.skill_id: s.proficiency for s in user_skills}
    
    score_achieved = 0.0
    score_max = 0.0
    
    for req in job.extracted_skills:
        score_max += req.weight
        user_prof = user_skill_dict.get(req.skill_id, 0)
        prof_ratio = min(user_prof / req.required_level, 1.0)
        score_achieved += (req.weight * prof_ratio)
        
    normalized_score = round(score_achieved / score_max, 2) if score_max > 0 else 0.0
    
    category = "Low Probability"
    if normalized_score >= 0.8:
        category = "Strong Match"
    elif normalized_score >= 0.5:
        category = "Reachable"
        
    return normalized_score, category

def recommend_jobs(user_skills: List[UserSkill], profile_embedding: Optional[List[float]]) -> List[Dict[str, Any]]:
    """
    Phase 6: Top Job Recommendations Engine
    Uses Neo4j Graph queries (Layer 1) to find overlapping skills,
    then adds Semantic Vector Similarity (Layer 2) if embedding is present.
    Creates a 'Why-Score' explanation.
    """
    candidate_skills = [s.name for s in user_skills]
    
    # Layer 1: Graph-Based Skill Overlap Score (Neo4j Cypher)
    query = """
    MATCH (j:Job)-[:REQUIRES_SKILL]->(s:Skill) 
    WHERE s.name IN $candidate_skills 
    WITH j, COUNT(s) AS matched_skills, j.total_required_skills AS total 
    WHERE total > 0
    RETURN j.title AS title, j.company AS company, j.apply_url AS apply_url, 
           (matched_skills * 1.0 / total) AS graph_score
    ORDER BY graph_score DESC LIMIT 20
    """
    
    graph_results = []
    try:
        graph_results = run_query(query, parameters={"candidate_skills": candidate_skills})
    except Exception as e:
        print(f"Neo4j recommendation failed: {e}")
        return []

    recommendations = []
    for row in graph_results:
        graph_score = row["graph_score"] or 0
        final_score = graph_score # Basic layer 1 score as fallback
        
        # In a full implementation, Layer 2: Vector similarity would be done here by fetching job embedding
        # and checking cosine similarity with profile_embedding. For now we use the graph score.
        
        # Generate 'Why-Score' Explanation
        explanation = []
        if graph_score >= 0.8:
            explanation.append("You match highly with the required skills for this role.")
        elif graph_score >= 0.5:
            explanation.append("Your skills are a decent fit, with some gaps.")
        else:
            explanation.append("You have a few matching skills but significant gaps remain.")
            
        recommendations.append({
            "title": row["title"],
            "company": row["company"],
            "apply_url": row["apply_url"],
            "match_ratio": round(final_score * 100, 1),
            "explanation": explanation
        })
        
    return recommendations

