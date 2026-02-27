from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router_resume, router_jobs, router_analysis
from app.core.config import settings


app = FastAPI(title=settings.PROJECT_NAME)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "skillgap-analyzer-api"}


app.include_router(router_resume.router, prefix=settings.API_PREFIX)
app.include_router(router_jobs.router, prefix=settings.API_PREFIX)
app.include_router(router_analysis.router, prefix=settings.API_PREFIX)

