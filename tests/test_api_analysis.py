from fastapi.testclient import TestClient

from app.main import app
from app.models.job import Job, JobRequirement
from app.models.skill import UserSkill
from app.models.user_profile import UserSkillProfile


client = TestClient(app)


def test_analyze_endpoint_basic():
    profile = UserSkillProfile(
        skills=[UserSkill(skill_id="python", name="Python", proficiency=3, evidence_count=2)]
    )
    job = Job(
        title="Backend Developer",
        extracted_skills=[JobRequirement(skill_id="python", weight=1.0, required_level=3)],
    )

    payload = {
        "profile": profile.model_dump(),
        "jobs": [job.model_dump()],
        "weekly_hours": 10,
    }

    response = client.post("/api/analyze/", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["fit_results"][0]["category"] == "Strong Match"
    assert data["gaps"] == [] or isinstance(data["gaps"], list)
    assert isinstance(data["roadmap"], list)

