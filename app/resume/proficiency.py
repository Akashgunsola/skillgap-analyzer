def estimate_proficiency(skill_freq: int):
    if skill_freq >= 5:
        return 4   # expert
    elif skill_freq >= 3:
        return 3   # strong
    elif skill_freq >= 1:
        return 2   # working knowledge
    else:
        return 1
