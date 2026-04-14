from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artifact
from app.db.session import get_db
from app.schemas.artifact import ArtifactResponse
from app.services.object_storage import ObjectStorageService

router = APIRouter(prefix="/chats", tags=["artifacts"])


@router.get("/{chat_id}/artifacts", response_model=list[ArtifactResponse])
def list_chat_artifacts(chat_id: UUID, db: Session = Depends(get_db)) -> list[ArtifactResponse]:
    stmt = select(Artifact).where(Artifact.chat_id == chat_id).order_by(Artifact.created_at.asc())
    artifacts = db.execute(stmt).scalars().all()
    return [ArtifactResponse.model_validate(item) for item in artifacts]


@router.get("/{chat_id}/artifacts/{artifact_id}/download")
def download_chat_artifact(
    chat_id: UUID,
    artifact_id: UUID,
    db: Session = Depends(get_db),
):
    stmt = select(Artifact).where(
        Artifact.id == artifact_id,
        Artifact.chat_id == chat_id,
    )
    artifact = db.execute(stmt).scalars().first()

    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    storage = ObjectStorageService()
    url = storage.generate_presigned_get_url(artifact.storage_key, expires_in=3600)

    return RedirectResponse(url=url, status_code=307)
