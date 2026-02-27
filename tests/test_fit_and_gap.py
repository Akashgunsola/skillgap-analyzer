import unittest

from app.models.skill import UserSkill
from app.models.job import Job, JobRequirement
from app.core.fit_engine import calculate_fit_score
from app.core.gap_analyzer import analyze_gaps


class TestFitAndGap(unittest.TestCase):
    def test_strong_match_fit_score(self):
        user_skills = [
            UserSkill(skill_id="python", name="Python", proficiency=4, evidence_count=5),
            UserSkill(skill_id="django", name="Django", proficiency=4, evidence_count=5),
        ]

        job = Job(
            title="Backend Developer",
            extracted_skills=[
                JobRequirement(skill_id="python", weight=1.0, required_level=3),
                JobRequirement(skill_id="django", weight=1.0, required_level=3),
            ],
        )

        score, category = calculate_fit_score(user_skills, job)

        self.assertGreaterEqual(score, 0.8)
        self.assertEqual(category, "Strong Match")

    def test_gap_analysis_identifies_missing_skill(self):
        user_skills = [
            UserSkill(skill_id="python", name="Python", proficiency=4, evidence_count=5),
        ]

        job = Job(
            title="Backend Developer",
            extracted_skills=[
                JobRequirement(skill_id="python", weight=1.0, required_level=3),
                JobRequirement(skill_id="django", weight=1.0, required_level=3),
            ],
        )

        gaps = analyze_gaps(user_skills, job)

        gap_skill_ids = {g["skill_id"] for g in gaps}
        self.assertIn("django", gap_skill_ids)


if __name__ == "__main__":
    unittest.main()

