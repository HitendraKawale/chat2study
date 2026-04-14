from __future__ import annotations

from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chat, Source
from app.services.providers import ProviderFactory
from app.workflows.ingestion_state import IngestionState


class IngestionNodes:
    def __init__(self, db: Session) -> None:
        self.db = db

    def load_chat(self, state: IngestionState) -> dict:
        chat_id = UUID(state["chat_id"])

        stmt = (
            select(Chat, Source)
            .join(Source, Chat.source_id == Source.id, isouter=True)
            .where(Chat.id == chat_id)
        )
        row = self.db.execute(stmt).first()

        if row is None:
            raise ValueError(f"Chat not found: {chat_id}")

        chat, source = row

        source_url = source.source_url if source else ""
        source_type = source.source_type if source else "unknown"
        source_domain = source.source_domain if source else (urlparse(source_url).netloc or None)

        return {
            "title": chat.title,
            "source_url": source_url,
            "source_type": source_type,
            "source_domain": source_domain,
            "status": "loaded",
        }

    def select_providers(self, state: IngestionState) -> dict:
        chat_provider = ProviderFactory.default_chat_provider()
        embedding_provider = ProviderFactory.default_embedding_provider()

        return {
            "selected_chat_provider": chat_provider,
            "selected_embedding_provider": embedding_provider,
            "selected_chat_model": ProviderFactory.resolve_chat_model_name(chat_provider),
            "selected_embedding_model": ProviderFactory.resolve_embedding_model_name(
                embedding_provider
            ),
            "status": "providers_selected",
        }

    def plan_capture(self, state: IngestionState) -> dict:
        domain = (state.get("source_domain") or "").lower()
        source_type = state.get("source_type", "unknown")

        known_auth_domains = {
            "chatgpt.com",
            "claude.ai",
            "gemini.google.com",
        }

        capture_strategy = (
            "playwright_authenticated_browser"
            if domain in known_auth_domains
            else "playwright_generic_browser"
        )

        planned_artifacts = [
            "raw_html",
            "visible_text",
            "screenshot_png",
            "snapshot_pdf",
        ]

        if source_type != "web_chat_url":
            planned_artifacts.append("source_metadata_json")

        return {
            "capture_strategy": capture_strategy,
            "planned_artifacts": planned_artifacts,
            "status": "capture_planned",
        }

    def classify_complexity_seed(self, state: IngestionState) -> dict:
        title = (state.get("title") or "").lower()
        domain = (state.get("source_domain") or "").lower()

        keywords = {
            "agent",
            "rag",
            "transformer",
            "langgraph",
            "pipeline",
            "embedding",
            "vector",
            "async",
            "architecture",
            "reasoning",
            "evaluation",
        }

        score = 2

        if domain in {"chatgpt.com", "claude.ai", "gemini.google.com"}:
            score += 2

        for keyword in keywords:
            if keyword in title:
                score += 1

        score = min(score, 10)

        return {
            "complexity_score": score,
            "should_generate_notes": score >= 5,
            "should_generate_visual_notes": score >= 6,
            "status": "complexity_seeded",
        }

    def build_result_payload(self, state: IngestionState) -> dict:
        payload = {
            "chat_id": state["chat_id"],
            "job_id": state["job_id"],
            "title": state.get("title"),
            "source_url": state.get("source_url"),
            "source_type": state.get("source_type"),
            "source_domain": state.get("source_domain"),
            "selected_chat_provider": state.get("selected_chat_provider"),
            "selected_embedding_provider": state.get("selected_embedding_provider"),
            "selected_chat_model": state.get("selected_chat_model"),
            "selected_embedding_model": state.get("selected_embedding_model"),
            "capture_strategy": state.get("capture_strategy"),
            "planned_artifacts": state.get("planned_artifacts", []),
            "complexity_score": state.get("complexity_score"),
            "should_generate_notes": state.get("should_generate_notes", False),
            "should_generate_visual_notes": state.get("should_generate_visual_notes", False),
        }

        return {
            "result_payload": payload,
            "status": "planned",
        }
