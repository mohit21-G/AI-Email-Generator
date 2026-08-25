from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from core.config import settings

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str = "healthy"


class ReadinessCheckResponse(BaseModel):
    status: str = "ready"
    checks: dict


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Health Check",
    description="Returns simple healthy status to verify service container liveness.",
)
async def health_check():
    return {"status": "healthy"}


@router.get(
    "/ready",
    response_model=ReadinessCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Health Check",
    description="Verifies whether environment configuration and required dependencies are available.",
)
async def readiness_check():
    cohere_key_set = bool(settings.COHERE_API_KEY and settings.COHERE_API_KEY.strip())
    api_key_set = bool(settings.API_KEY and settings.API_KEY.strip())

    is_ready = cohere_key_set and api_key_set

    checks = {
        "cohere_api_key_configured": cohere_key_set,
        "api_key_configured": api_key_set,
    }

    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "Service is not ready. Missing required environment configuration.",
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "checks": checks,
    }
