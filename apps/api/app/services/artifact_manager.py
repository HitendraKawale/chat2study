from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Artifact
from app.services.object_storage import ObjectStorageService


class ArtifactManager:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = ObjectStorageService()

    def upload_and_record(
        self,
        chat_id: UUID,
        artifact_type: str,
        local_path: Path,
        content_type: str,
    ) -> Artifact:
        object_key = f"chats/{chat_id}/{local_path.name}"
        self.storage.upload_file(local_path, object_key, content_type)

        artifact = Artifact(
            chat_id=chat_id,
            artifact_type=artifact_type,
            storage_key=object_key,
            mime_type=content_type,
            size_bytes=local_path.stat().st_size if local_path.exists() else None,
        )
        self.db.add(artifact)
        self.db.flush()
        return artifact
