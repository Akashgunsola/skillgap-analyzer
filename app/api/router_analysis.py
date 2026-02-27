from typing import List

from fastapi import APIRouter

from app.core.fit_engine import calculate_fit_score
from app.core.gap_analyzer import analyze_gaps
from app.core.roadmap_generator import generate_roadmap
from app.models.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    FitScorePerJob,
    GapItem,
    RoadmapItem,
)
from app.models.skill import UserSkill


router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.get("/health")
def analysis_health_check() -> dict:
    return {"status": "ok", "component": "analysis"}


@router.post("/", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """
    Compute job fit scores, skill gaps, and a learning roadmap for a user profile and target jobs.
    """
    user_skills: List[UserSkill] = request.profile.skills

    fit_results: List[FitScorePerJob] = []
    all_gaps: List[GapItem] = []

    for job in request.jobs:
        score, category = calculate_fit_score(user_skills, job)
        fit_results.append(FitScorePerJob(job=job, fit_score=score, category=category))

        gap_dicts = analyze_gaps(user_skills, job)
        for g in gap_dicts:
            all_gaps.append(
                GapItem(
                    skill_id=g["skill_id"],
                    name=g["name"],
                    weight=g["weight"],
                    difficulty=g["difficulty"],
                    learning_hours=g["learning_hours"],
                    gap_score=g["gap_score"],
                )
            )

    # De-duplicate gaps across jobs by keeping the highest gap_score
    dedup_gaps: dict[str, GapItem] = {}
    for gap in all_gaps:
        existing = dedup_gaps.get(gap.skill_id)
        if existing is None or gap.gap_score > existing.gap_score:
            dedup_gaps[gap.skill_id] = gap

    ordered_gaps = sorted(
        dedup_gaps.values(), key=lambda g: g.gap_score, reverse=True
    )

    # Use existing roadmap generator which expects list of dicts
    roadmap_input = [
        {
            "skill_id": g.skill_id,
            "name": g.name,
            "gap_score": g.gap_score,
            "learning_hours": g.learning_hours,
        }
        for g in ordered_gaps
    ]
    roadmap_dicts = generate_roadmap(roadmap_input)

    roadmap: List[RoadmapItem] = [
        RoadmapItem(
            timeframe=r["timeframe"],
            learning_focus=r["skill_name"],
            learning_hours=r["learning_hours"],
            priority_score=r["priority_score"],
        )
        for r in roadmap_dicts
    ]

    return AnalysisResponse(
        fit_results=fit_results,
        gaps=ordered_gaps,
        roadmap=roadmap,
    )


