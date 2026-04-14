from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Artifact, Chat, Chunk
from app.services.chunking import TextChunkingService
from app.services.object_storage import ObjectStorageService
from app.services.providers import ProviderFactory


class ChatIndexingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = ObjectStorageService()
        self.chunker = TextChunkingService()

    def index_chat(self, chat_id: UUID) -> dict[str, Any]:
        chat = self.db.get(Chat, chat_id)
        if chat is None:
            raise ValueError(f"Chat not found: {chat_id}")

        artifact_stmt = (
            select(Artifact)
            .where(
                Artifact.chat_id == chat_id,
                Artifact.artifact_type == "visible_text",
            )
            .order_by(Artifact.created_at.desc())
        )
        artifact = self.db.execute(artifact_stmt).scalars().first()

        if artifact is None:
            raise ValueError("No visible_text artifact found for this chat")

        text = self.storage.read_text(artifact.storage_key)
        chunks = self.chunker.split(text)

        if not chunks:
            raise ValueError("No chunks could be generated from the text artifact")

        embedding_provider = ProviderFactory.default_embedding_provider()
        embedding_model_name = ProviderFactory.resolve_embedding_model_name(embedding_provider)
        embedding_model = ProviderFactory.get_embedding_model(embedding_provider)

        texts = [chunk["text"] for chunk in chunks]
        vectors = embedding_model.embed_documents(texts)

        if not vectors:
            raise ValueError("Embedding provider returned no vectors")

        if len(vectors[0]) != settings.embedding_dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {settings.embedding_dimensions}, "
                f"got {len(vectors[0])}"
            )

        self.db.execute(delete(Chunk).where(Chunk.chat_id == chat_id))
        self.db.flush()

        for chunk_data, vector in zip(chunks, vectors, strict=True):
            row = Chunk(
                chat_id=chat.id,
                ordinal=chunk_data["ordinal"],
                text=chunk_data["text"],
                token_count=chunk_data["token_count"],
                embedding_provider=embedding_provider,
                embedding_model=embedding_model_name,
                embedding_dimensions=len(vector),
                embedding=list(vector),
                metadata_json=chunk_data["metadata_json"],
            )
            self.db.add(row)

        chat.status = "indexed"
        self.db.commit()

        return {
            "chat_id": str(chat.id),
            "status": chat.status,
            "chunk_count": len(chunks),
            "embedding_provider": embedding_provider,
            "embedding_model": embedding_model_name,
            "embedding_dimensions": len(vectors[0]),
        }
