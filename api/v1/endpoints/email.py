from fastapi import APIRouter, HTTPException, Request, Security, status
from core.config import settings
from core.limiter import limiter
from core.security import verify_api_key
from schemas.email import (
    APIErrorResponse,
    EmailGenerateRequest,
    EmailGenerateResponse,
)
from services.email_service import EmailService

router = APIRouter()


@router.post(
    "/generate",
    response_model=EmailGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Email",
    description="Generate a professional email based on topic, sender, recipient, and style parameters.",
    responses={
        200: {"model": EmailGenerateResponse, "description": "Email generated successfully"},
        401: {"model": APIErrorResponse, "description": "Unauthorized - Missing or invalid API key"},
        422: {"model": APIErrorResponse, "description": "Unprocessable Entity - Request validation error"},
        429: {"model": APIErrorResponse, "description": "Too Many Requests - Rate limit exceeded"},
        500: {"model": APIErrorResponse, "description": "Internal Server Error"},
        503: {"model": APIErrorResponse, "description": "Service Unavailable"},
    },
)
@limiter.limit(settings.RATE_LIMIT)
async def generate_email(
    request: Request,
    payload: EmailGenerateRequest,
    api_key: str = Security(verify_api_key),
) -> EmailGenerateResponse:
    """
    Endpoint to generate an AI email.
    Requires header: X-API-Key
    """
    try:
        response = EmailService.generate_email(payload)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while generating the email.",
        )
