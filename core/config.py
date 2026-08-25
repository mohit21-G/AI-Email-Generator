import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Email Generator API")
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-ready REST API for AI Email Generator using Cohere model."
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    API_KEY: str = os.getenv("API_KEY", "email-gen-secret-key-2026")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    API_URL: str = os.getenv("API_URL", "http://localhost:8000/api/v1")

    # Rate Limiting & Security
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10 per minute")

    @property
    def allowed_origins(self) -> List[str]:
        raw_origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8501,http://127.0.0.1:8501,http://localhost:8000,http://127.0.0.1:8000",
        )
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


settings = Settings()
