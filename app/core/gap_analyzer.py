from typing import List, Dict
from app.models.skill import UserSkill
from app.models.job import Job
from app.skills.loader import load_skills

def analyze_gaps(user_skills: List[UserSkill], job: Job) -> List[Dict]:
    """
    Identifies missing skills for a given job and ranks them by learning ROI (Gap Score).
    
    Gap Score = importance_weight * (difficulty / learning_hours)
    """
    skill_map, _ = load_skills()
    user_skill_ids = {s.skill_id for s in user_skills}
    
    gaps = []
    
    for req in job.extracted_skills:
        if req.skill_id not in user_skill_ids:
            skill_meta = skill_map.get(req.skill_id)
            if not skill_meta:
                continue
                
            difficulty = skill_meta.get("difficulty", 2)
            learning_hours = skill_meta.get("learning_hours", 40)
            
            # Avoid division by zero
            if learning_hours == 0:
                learning_hours = 1
                
            gap_score = (req.weight * difficulty) / learning_hours
            
            gaps.append({
                "skill_id": req.skill_id,
                "name": skill_meta.get("name", req.skill_id),
                "weight": req.weight,
                "difficulty": difficulty,
                "learning_hours": learning_hours,
                "gap_score": gap_score
            })
            
    # Sort DESCENDING by gap_score (highest ROI first)
    gaps.sort(key=lambda x: x["gap_score"], reverse=True)
    
    return gaps
