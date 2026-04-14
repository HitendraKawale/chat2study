from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "api",
        "project": settings.project_name,
        "environment": settings.app_env,
        "chat_provider": settings.default_chat_provider,
        "embedding_provider": settings.default_embedding_provider,
    }
