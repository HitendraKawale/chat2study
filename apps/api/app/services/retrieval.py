from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Chat, Chunk
from app.services.providers import ProviderFactory


class ChatRetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def search(
        self,
        chat_id: UUID,
        query: str,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        chat = self.db.get(Chat, chat_id)
        if chat is None:
            raise ValueError(f"Chat not found: {chat_id}")

        final_top_k = top_k or settings.retrieval_top_k

        embedding_provider = ProviderFactory.default_embedding_provider()
        embedding_model = ProviderFactory.get_embedding_model(embedding_provider)
        query_vector = embedding_model.embed_query(query)

        if len(query_vector) != settings.embedding_dimensions:
            raise ValueError(
                f"Query embedding dimension mismatch: expected {settings.embedding_dimensions}, "
                f"got {len(query_vector)}"
            )

        distance_expr = Chunk.embedding.cosine_distance(list(query_vector))

        stmt = (
            select(Chunk, distance_expr.label("distance"))
            .where(Chunk.chat_id == chat_id)
            .order_by(distance_expr)
            .limit(final_top_k)
        )
        rows = self.db.execute(stmt).all()

        matches = [
            {
                "chunk_id": str(chunk.id),
                "ordinal": chunk.ordinal,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "distance": float(distance),
                "metadata_json": chunk.metadata_json or {},
            }
            for chunk, distance in rows
        ]

        return {
            "chat_id": str(chat.id),
            "query": query,
            "top_k": final_top_k,
            "matches": matches,
        }
