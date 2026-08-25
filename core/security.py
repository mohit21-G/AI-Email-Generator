from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Validates incoming X-API-Key HTTP header against configured settings.API_KEY.
    Raises HTTP 401 Unauthorized if missing or invalid.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header 'X-API-Key' is missing",
        )
    if api_key_header != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key provided",
        )
    return api_key_header
