from typing import List


class Settings:
    PROJECT_NAME: str = "SkillGap Analyzer API"
    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()

