from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artifact
from app.db.session import get_db
from app.schemas.artifact import ArtifactResponse

router = APIRouter(prefix="/chats", tags=["artifacts"])


@router.get("/{chat_id}/artifacts", response_model=list[ArtifactResponse])
def list_chat_artifacts(chat_id: UUID, db: Session = Depends(get_db)) -> list[ArtifactResponse]:
    stmt = select(Artifact).where(Artifact.chat_id == chat_id).order_by(Artifact.created_at.asc())
    artifacts = db.execute(stmt).scalars().all()
    return [ArtifactResponse.model_validate(item) for item in artifacts]
