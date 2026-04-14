from __future__ import annotations

import json
import re
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Artifact, Chat, Chunk, Note
from app.schemas.notes import VisualNotesDocument
from app.services.object_storage import ObjectStorageService
from app.services.providers import ProviderFactory

STUDY_NOTE_TYPE = "study_notes"
VISUAL_NOTE_TYPE = "visual_notes"


def _coerce_content(value: Any) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()

    return str(value)


def _extract_json_block(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Could not locate a JSON object in model output")

    return json.loads(cleaned[start : end + 1])


class ChatNotesService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = ObjectStorageService()

    def _load_context(self, chat_id: UUID) -> tuple[Chat, str]:
        chat = self.db.get(Chat, chat_id)
        if chat is None:
            raise ValueError(f"Chat not found: {chat_id}")

        chunk_stmt = select(Chunk).where(Chunk.chat_id == chat_id).order_by(Chunk.ordinal.asc())
        chunks = self.db.execute(chunk_stmt).scalars().all()

        if chunks:
            parts: list[str] = []
            total_chars = 0

            for chunk in chunks:
                chunk_text = chunk.text.strip()
                if not chunk_text:
                    continue

                remaining = settings.notes_context_char_limit - total_chars
                if remaining <= 0:
                    break

                clipped = chunk_text[:remaining]
                parts.append(clipped)
                total_chars += len(clipped) + 2

            context = "\n\n".join(parts).strip()
            if context:
                return chat, context

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
            raise ValueError("No indexed chunks or visible_text artifact found")

        text = self.storage.read_text(artifact.storage_key)
        return chat, text[: settings.notes_context_char_limit].strip()

    def _upsert_note(
        self,
        chat_id: UUID,
        note_type: str,
        *,
        content_md: str | None,
        content_json: dict[str, Any] | None,
        model_provider: str,
        model_name: str,
    ) -> Note:
        stmt = select(Note).where(
            Note.chat_id == chat_id,
            Note.note_type == note_type,
        )
        note = self.db.execute(stmt).scalars().first()

        if note is None:
            note = Note(
                chat_id=chat_id,
                note_type=note_type,
                content_md=content_md,
                content_json=content_json,
                model_provider=model_provider,
                model_name=model_name,
            )
            self.db.add(note)
        else:
            note.content_md = content_md
            note.content_json = content_json
            note.model_provider = model_provider
            note.model_name = model_name

        self.db.commit()
        self.db.refresh(note)
        return note

    def generate_study_notes(self, chat_id: UUID) -> Note:
        chat, context = self._load_context(chat_id)

        provider = ProviderFactory.default_chat_provider()
        model_name = ProviderFactory.resolve_chat_model_name(provider)
        model = ProviderFactory.get_chat_model(provider)

        prompt = f"""
You are generating study notes from an indexed technical chat.

Rules:
- Use only the supplied chat context.
- Output markdown only.
- Keep it concise but useful.
- Include these sections:
  1. Summary
  2. Core Ideas
  3. Important Decisions
  4. Key Terms
  5. Open Questions
  6. Suggested Follow-ups
- Do not invent facts not present in the context.

Chat title:
{chat.title}

Context:
{context}
""".strip()

        response = model.invoke(prompt)
        markdown = _coerce_content(response.content).strip()

        if not markdown:
            raise ValueError("Study note generation returned empty content")

        return self._upsert_note(
            chat.id,
            STUDY_NOTE_TYPE,
            content_md=markdown,
            content_json=None,
            model_provider=provider,
            model_name=model_name,
        )

    def generate_visual_notes(self, chat_id: UUID) -> Note:
        chat, context = self._load_context(chat_id)

        provider = ProviderFactory.default_chat_provider()
        model_name = ProviderFactory.resolve_chat_model_name(provider)
        model = ProviderFactory.get_chat_model(provider)

        base_prompt = f"""
Generate a compact visual study map for a technical chat.

Ground rules:
- Stay grounded only in the supplied context.
- Produce 3 to 6 summary cards.
- Produce 4 to 8 concept nodes.
- Produce 3 to 10 edges.
- Keep labels short and readable.
- Suggested questions should help a learner explore the topic further.

Chat title:
{chat.title}

Context:
{context}
""".strip()

        try:
            structured_model = model.with_structured_output(VisualNotesDocument)
            document = structured_model.invoke(base_prompt)

            if not isinstance(document, VisualNotesDocument):
                document = VisualNotesDocument.model_validate(document)
        except Exception:
            schema_hint = {
                "title": "Short title",
                "summary": "One paragraph summary",
                "cards": [{"title": "Card title", "body": "Short explanation"}],
                "nodes": [{"id": "node_1", "label": "Concept", "kind": "concept"}],
                "edges": [{"source": "node_1", "target": "node_2", "label": "relates to"}],
                "suggested_questions": ["What should I study next?"],
            }

            fallback_prompt = f"""
{base_prompt}

Return ONLY valid JSON.
Use exactly this shape:
{json.dumps(schema_hint, indent=2)}
""".strip()

            response = model.invoke(fallback_prompt)
            payload = _extract_json_block(_coerce_content(response.content))
            document = VisualNotesDocument.model_validate(payload)

        return self._upsert_note(
            chat.id,
            VISUAL_NOTE_TYPE,
            content_md=None,
            content_json=document.model_dump(),
            model_provider=provider,
            model_name=model_name,
        )

    def get_notes_bundle(self, chat_id: UUID) -> dict[str, Note | None]:
        study_stmt = select(Note).where(
            Note.chat_id == chat_id,
            Note.note_type == STUDY_NOTE_TYPE,
        )
        visual_stmt = select(Note).where(
            Note.chat_id == chat_id,
            Note.note_type == VISUAL_NOTE_TYPE,
        )

        study = self.db.execute(study_stmt).scalars().first()
        visual = self.db.execute(visual_stmt).scalars().first()

        return {
            "study_notes": study,
            "visual_notes": visual,
        }
