from typing import List, Tuple
from app.models.skill import UserSkill
from app.models.job import Job

def calculate_fit_score(user_skills: List[UserSkill], job: Job) -> Tuple[float, str]:
    """
    Calculates the fit score between a user's skills and a job's requirements.
    
    Fit Score = sum(job_skill_weight * min(user_proficiency / required_level, 1))
    Max possible score assumes 100% proficiency match for all required skills.
    Returns (normalized_score, category_label)
    """
    if not job.extracted_skills:
        return 0.0, "Low Probability"

    user_skill_dict = {s.skill_id: s.proficiency for s in user_skills}
    
    score_achieved = 0.0
    score_max = 0.0
    
    for req in job.extracted_skills:
        score_max += req.weight
        
        user_prof = user_skill_dict.get(req.skill_id, 0)
        
        # Calculate proficiency ratio maxing out at 1.0 (no extra credit for over-qualification)
        prof_ratio = min(user_prof / req.required_level, 1.0)
        score_achieved += (req.weight * prof_ratio)
        
    normalized_score = round(score_achieved / score_max, 2) if score_max > 0 else 0.0
    
    category = "Low Probability"
    if normalized_score >= 0.8:
        category = "Strong Match"
    elif normalized_score >= 0.5:
        category = "Reachable"
        
    return normalized_score, category
