from rapidfuzz import fuzz
from app.skills.loader import load_skills
from app.models.job import JobRequirement
from typing import List

SKILL_MAP, ALIAS_MAP = load_skills()

def extract_job_requirements(text: str) -> List[JobRequirement]:
    """
    Extracts skills from a job description text and computes their relative importance weights.
    Returns a list of JobRequirement models.
    """
    found_counts = {}
    words = text.split()
    
    # Basic n-gram search for skills (up to 3 words)
    for i in range(len(words)):
        phrase = " ".join(words[i:min(i+3, len(words))])
        
        for alias, skill_id in ALIAS_MAP.items():
            score = fuzz.partial_ratio(alias, phrase)
            if score > 85:
                found_counts[skill_id] = found_counts.get(skill_id, 0) + 1

    requirements = []
    
    if not found_counts:
        return requirements
        
    # Calculate weights based on frequency. 
    # Max frequency gets weight of 1.0, others are proportional.
    max_freq = max(found_counts.values())
    
    for skill_id, count in found_counts.items():
        # Baseline weight + normalized frequency weight
        weight = 0.5 + (0.5 * (count / max_freq))
        
        # Determine required level heuristically (default 3, might increase if mentioned often)
        req_level = 3
        if count >= 3:
            req_level = 4
            
        requirements.append(
            JobRequirement(
                skill_id=skill_id,
                weight=round(weight, 2),
                required_level=req_level
            )
        )
        
    # Deduplicate by skill_id taking the highest weight
    deduped = {}
    for req in requirements:
        if req.skill_id not in deduped or req.weight > deduped[req.skill_id].weight:
            deduped[req.skill_id] = req
            
    return list(deduped.values())
