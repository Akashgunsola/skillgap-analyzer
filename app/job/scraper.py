import uuid
from datetime import datetime
from celery import shared_task

from app.skills.neo4j_client import run_query
from app.resume.extractor import extract_skills_and_embedding

@shared_task
def fetch_jobs():
    """
    Mock job fetching task. In a real scenario, this would call boards like LinkedIn or Adzuna.
    For Phase 5, this demonstrates the enrichment pipeline feeding Neo4j.
    """
    # Dummy jobs fetched from an API
    jobs = [
        {
            "id": str(uuid.uuid4()),
            "title": "Machine Learning Engineer",
            "company": "TechCorp",
            "description": "We need a Machine Learning Engineer proficient in Python and SQL. Experience with Django is a plus.",
            "url": "https://example.com/job/1"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Full Stack Developer",
            "company": "WebWorks",
            "description": "Looking for a full stack dev. Must know Javascript and Python.",
            "url": "https://example.com/job/2"
        }
    ]

    for job in jobs:
        print(f"Processing job: {job['title']}")
        
        # Step 1: Run NLP on job description
        skills_found, embedding = extract_skills_and_embedding(job["description"])
        
        # Step 2: Save job node to Neo4j
        query_job = """
        MERGE (j:Job {id: $job_id})
        SET j.title = $title,
            j.company = $company,
            j.apply_url = $url,
            j.posted_date = $date,
            j.total_required_skills = $total_skills
        """
        run_query(query_job, parameters={
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "url": job["url"],
            "date": datetime.utcnow().isoformat(),
            "total_skills": len(skills_found)
        })
        
        # Step 3: Link job to skills
        for skill_id, frequency in skills_found.items():
            query_edge = """
            MATCH (j:Job {id: $job_id}), (s:Skill {skill_id: $skill_id})
            MERGE (j)-[r:REQUIRES_SKILL]->(s)
            SET r.frequency = $frequency,
                r.weight = 0.8  // default weight for parsed skills
            """
            run_query(query_edge, parameters={
                "job_id": job["id"],
                "skill_id": skill_id,
                "frequency": frequency
            })

    return f"Processed {len(jobs)} jobs"
