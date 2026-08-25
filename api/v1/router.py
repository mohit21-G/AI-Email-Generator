from fastapi import APIRouter
from api.v1.endpoints import email, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(email.router, prefix="/email", tags=["Email Generation"])
