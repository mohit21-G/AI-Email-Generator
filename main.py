import time
import uuid
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from api.v1.endpoints.health import router as health_router
from api.v1.router import api_router
from core.config import settings
from core.limiter import limiter
from core.logging import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable Proxy Headers for Reverse Proxies (HTTPS / Load Balancers)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Register SlowAPI Limiter state
app.state.limiter = limiter

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging & Request ID Middleware


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    logger.info(f"--> [{request_id}] {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        logger.info(f"<-- [{request_id}] {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"<-- [{request_id}] {request.method} {request.url.path} - Error: {str(exc)} ({process_time:.2f}ms)", exc_info=True)
        raise exc


# Rate Limit Exception Handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "message": "Rate limit exceeded",
            "data": None,
            "error": {
                "code": "TOO_MANY_REQUESTS",
                "detail": f"Rate limit exceeded: {exc.detail}",
            },
        },
    )


# Custom Exception Handlers for Standard JSON Responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code_map = {
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    error_code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
            "data": None,
            "error": {
                "code": error_code,
                "detail": exc.detail,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []
    for err in errors:
        loc = " -> ".join([str(p) for p in err.get("loc", [])])
        msg = err.get("msg", "Validation error")
        formatted_errors.append({"location": loc, "message": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Invalid request payload",
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "detail": formatted_errors,
            },
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "detail": "An unexpected server error occurred.",
            },
        },
    )


# Top-level Health Checks (/health and /ready)
app.include_router(health_router)

# Include API v1 Router (/api/v1/...)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {
        "success": True,
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "data": {
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "api_v1": f"{settings.API_PREFIX}/email/generate",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
