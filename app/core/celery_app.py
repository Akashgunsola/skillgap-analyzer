import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "skillgap_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.job.scraper"]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Optional: Configure periodic tasks using CELERYBEAT_SCHEDULE
celery_app.conf.beat_schedule = {
    'scrape-daily-jobs': {
        'task': 'app.job.scraper.fetch_jobs',
        'schedule': 86400.0, # Run every 24 hours
    },
}
