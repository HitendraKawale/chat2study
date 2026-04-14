from fastapi import APIRouter

from app.api.routes.artifacts import router as artifacts_router
from app.api.routes.chats import router as chats_router
from app.api.routes.health import router as health_router
from app.api.routes.indexing import router as indexing_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.providers import router as providers_router
from app.api.routes.retrieval import router as retrieval_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/api/v1")
api_router.include_router(chats_router, prefix="/api/v1")
api_router.include_router(jobs_router, prefix="/api/v1")
api_router.include_router(providers_router, prefix="/api/v1")
api_router.include_router(ingestion_router, prefix="/api/v1")
api_router.include_router(artifacts_router, prefix="/api/v1")
api_router.include_router(indexing_router, prefix="/api/v1")
api_router.include_router(retrieval_router, prefix="/api/v1")

