from fastapi import APIRouter

from app.api.routes.chats import router as chats_router
from app.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/api/v1")
api_router.include_router(chats_router, prefix="/api/v1")

