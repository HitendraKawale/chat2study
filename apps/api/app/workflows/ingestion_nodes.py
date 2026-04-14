from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chat, Source
from app.services.artifact_manager import ArtifactManager
from app.services.capture.browser_capture import BrowserCaptureService
from app.services.indexing import ChatIndexingService
from app.services.notes import ChatNotesService
from app.services.providers import ProviderFactory
from app.workflows.ingestion_state import IngestionState


class IngestionNodes:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.capture = BrowserCaptureService()
        self.artifacts = ArtifactManager(db)
        self.indexing = ChatIndexingService(db)
        self.notes = ChatNotesService(db)

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

    def execute_capture(self, state: IngestionState) -> dict:
        artifacts = self.capture.capture_chat(
            chat_id=state["chat_id"],
            source_url=state["source_url"],
            capture_strategy=state["capture_strategy"],
        )

        return {
            "title": artifacts.title,
            "final_url": artifacts.final_url,
            "staged_html_path": str(artifacts.html_path),
            "staged_text_path": str(artifacts.text_path),
            "staged_screenshot_path": str(artifacts.screenshot_path),
            "staged_pdf_path": str(artifacts.pdf_path),
            "status": "captured",
        }

    def persist_artifacts(self, state: IngestionState) -> dict:
        chat_id = UUID(state["chat_id"])

        saved = []

        mapping = [
            ("raw_html", Path(state["staged_html_path"]), "text/html"),
            ("visible_text", Path(state["staged_text_path"]), "text/plain"),
            ("screenshot_png", Path(state["staged_screenshot_path"]), "image/png"),
            ("snapshot_pdf", Path(state["staged_pdf_path"]), "application/pdf"),
        ]

        for artifact_type, local_path, content_type in mapping:
            artifact = self.artifacts.upload_and_record(
                chat_id=chat_id,
                artifact_type=artifact_type,
                local_path=local_path,
                content_type=content_type,
            )
            saved.append(
                {
                    "id": str(artifact.id),
                    "artifact_type": artifact.artifact_type,
                    "storage_key": artifact.storage_key,
                    "mime_type": artifact.mime_type,
                    "size_bytes": artifact.size_bytes,
                }
            )

        self.db.commit()

        return {
            "persisted_artifacts": saved,
            "status": "artifacts_persisted",
        }

    def index_chat(self, state: IngestionState) -> dict:
        result = self.indexing.index_chat(UUID(state["chat_id"]))

        return {
            "indexed_chunk_count": result["chunk_count"],
            "indexed_embedding_provider": result["embedding_provider"],
            "indexed_embedding_model": result["embedding_model"],
            "indexed_embedding_dimensions": result["embedding_dimensions"],
            "status": "indexed",
        }

    def classify_complexity_seed(self, state: IngestionState) -> dict:
        title = (state.get("title") or "").lower()
        domain = (state.get("source_domain") or "").lower()

        text_path = state.get("staged_text_path")
        text = ""
        if text_path:
            text = Path(text_path).read_text(encoding="utf-8", errors="ignore").lower()

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
            if keyword in title or keyword in text:
                score += 1

        if len(text.split()) > 2500:
            score += 2

        score = min(score, 10)

        return {
            "complexity_score": score,
            "should_generate_notes": score >= 5,
            "should_generate_visual_notes": score >= 6,
            "status": "complexity_seeded",
        }

    def generate_study_notes(self, state: IngestionState) -> dict:
        if not state.get("should_generate_notes", False):
            return {
                "study_notes_generated": False,
                "status": "study_notes_skipped",
            }

        note = self.notes.generate_study_notes(UUID(state["chat_id"]))

        return {
            "study_note_id": str(note.id),
            "study_notes_generated": True,
            "status": "study_notes_generated",
        }

    def generate_visual_notes(self, state: IngestionState) -> dict:
        if not state.get("should_generate_visual_notes", False):
            return {
                "visual_notes_generated": False,
                "status": "visual_notes_skipped",
            }

        note = self.notes.generate_visual_notes(UUID(state["chat_id"]))

        return {
            "visual_note_id": str(note.id),
            "visual_notes_generated": True,
            "status": "visual_notes_generated",
        }

    def build_result_payload(self, state: IngestionState) -> dict:
        payload = {
            "chat_id": state["chat_id"],
            "job_id": state["job_id"],
            "title": state.get("title"),
            "source_url": state.get("source_url"),
            "final_url": state.get("final_url"),
            "source_type": state.get("source_type"),
            "source_domain": state.get("source_domain"),
            "selected_chat_provider": state.get("selected_chat_provider"),
            "selected_embedding_provider": state.get("selected_embedding_provider"),
            "selected_chat_model": state.get("selected_chat_model"),
            "selected_embedding_model": state.get("selected_embedding_model"),
            "capture_strategy": state.get("capture_strategy"),
            "planned_artifacts": state.get("planned_artifacts", []),
            "persisted_artifacts": state.get("persisted_artifacts", []),
            "indexed_chunk_count": state.get("indexed_chunk_count"),
            "indexed_embedding_provider": state.get("indexed_embedding_provider"),
            "indexed_embedding_model": state.get("indexed_embedding_model"),
            "indexed_embedding_dimensions": state.get("indexed_embedding_dimensions"),
            "complexity_score": state.get("complexity_score"),
            "should_generate_notes": state.get("should_generate_notes", False),
            "should_generate_visual_notes": state.get("should_generate_visual_notes", False),
            "study_note_id": state.get("study_note_id"),
            "study_notes_generated": state.get("study_notes_generated", False),
            "visual_note_id": state.get("visual_note_id"),
            "visual_notes_generated": state.get("visual_notes_generated", False),
        }

        return {
            "result_payload": payload,
            "status": "ready",
        }
