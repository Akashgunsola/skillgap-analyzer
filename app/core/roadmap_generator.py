from typing import List, Dict

HOURS_PER_WEEK = 15 # Assumed learning pacing

def generate_roadmap(missing_skills: List[Dict]) -> List[Dict]:
    """
    Creates an ordered learning plan tailored to the user's skill gaps.
    Schedules skills across weeks based on estimated required learning hours.
    Assumes missing_skills is already prioritized by Gap Score.
    """
    roadmap = []
    current_week = 1
    hours_in_current_week = 0
    
    for gap in missing_skills:
        skill_hours = gap["learning_hours"]
        
        # Calculate how many weeks this skill will take
        weeks_required = skill_hours / HOURS_PER_WEEK
        
        start_week = current_week
        end_week = start_week + int(weeks_required)
        
        timeframe = f"Week {start_week}" if start_week == end_week else f"Week {start_week}-{end_week}"
        
        roadmap.append({
            "timeframe": timeframe,
            "skill_name": gap["name"],
            "learning_hours": skill_hours,
            "priority_score": round(gap["gap_score"], 4)
        })
        
        # Update trackers
        current_week = end_week + 1
        
    return roadmap
