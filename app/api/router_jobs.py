from typing import List

from fastapi import APIRouter

from app.job.cleaner import clean_job_text
from app.job.extractor import extract_job_requirements
from app.models.analysis import JobInput, JobListRequest, JobListResponse
from app.models.job import Job


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/health")
def jobs_health_check() -> dict:
    return {"status": "ok", "component": "jobs"}


@router.post("/extract", response_model=JobListResponse)
def extract_jobs(request: JobListRequest) -> JobListResponse:
    """
    Normalize raw job descriptions into structured Job models with skill requirements.
    """
    jobs: List[Job] = []

    for item in request.jobs:
        cleaned = clean_job_text(item.description)
        requirements = extract_job_requirements(cleaned)
        jobs.append(Job(title=item.title, extracted_skills=requirements))

    return JobListResponse(jobs=jobs)


