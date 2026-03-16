from pathlib import Path
import tempfile
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.analysis import ResumeUploadResponse
from app.models.skill import UserSkill
from app.models.user_profile import UserSkillProfile
from app.resume.cleaner import clean_text
from app.resume.extractor import extract_skills_and_embedding
from app.resume.normalizer import normalize_skills
from app.resume.parser import parse_resume
from app.resume.proficiency import estimate_proficiency


router = APIRouter(prefix="/resume", tags=["resume"])


@router.get("/health")
def resume_health_check() -> dict:
    return {"status": "ok", "component": "resume"}


def _profile_from_text(raw_text: str) -> UserSkillProfile:
    cleaned = clean_text(raw_text)
    raw_skills, embedding = extract_skills_and_embedding(cleaned)
    normalized = normalize_skills(raw_skills)

    skills = [
        UserSkill(
            skill_id=s["skill_id"],
            name=s["name"],
            proficiency=estimate_proficiency(s["frequency"]),
            evidence_count=s["frequency"],
        )
        for s in normalized
    ]

    return UserSkillProfile(skills=skills, embedding=embedding)


@router.post(
    "/parse",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def parse_resume_endpoint(
    file: Optional[UploadFile] = File(default=None),
    text: Optional[str] = Form(default=None),
) -> ResumeUploadResponse:
    """
    Parse a resume (PDF/txt upload or raw text) into a structured user skill profile.
    """
    if file is None and (text is None or not text.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a resume file or resume text must be provided.",
        )

    if file is not None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".txt"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported resume format. Please upload a PDF or TXT file.",
            )

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            contents = await file.read()
            tmp.write(contents)
            tmp.close()
            raw_text = parse_resume(tmp.name)
        finally:
            Path(tmp.name).unlink(missing_ok=True)
    else:
        raw_text = text or ""

    profile = _profile_from_text(raw_text)
    return ResumeUploadResponse(profile=profile)


