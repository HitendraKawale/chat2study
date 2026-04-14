from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chat_id: UUID
    artifact_type: str
    storage_key: str
    mime_type: str | None
    size_bytes: int | None
    created_at: datetime
