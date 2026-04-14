from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chat_id: UUID
    job_type: str
    status: str
    attempts: int
    error_message: str | None
    result_payload: dict[str, Any] | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PersistedArtifactResponse(BaseModel):
    id: str
    artifact_type: str
    storage_key: str
    mime_type: str | None = None
    size_bytes: int | None = None


class IngestionWorkflowResponse(BaseModel):
    chat_id: str
    job_id: str
    title: str | None = None
    source_url: str | None = None
    final_url: str | None = None
    source_type: str | None = None
    source_domain: str | None = None
    selected_chat_provider: str | None = None
    selected_embedding_provider: str | None = None
    selected_chat_model: str | None = None
    selected_embedding_model: str | None = None
    capture_strategy: str | None = None
    planned_artifacts: list[str] = Field(default_factory=list)
    persisted_artifacts: list[PersistedArtifactResponse] = Field(default_factory=list)
    indexed_chunk_count: int | None = None
    indexed_embedding_provider: str | None = None
    indexed_embedding_model: str | None = None
    indexed_embedding_dimensions: int | None = None
    complexity_score: int | None = None
    should_generate_notes: bool = False
    should_generate_visual_notes: bool = False
    study_note_id: str | None = None
    study_notes_generated: bool = False
    visual_note_id: str | None = None
    visual_notes_generated: bool = False


class IngestionRunResponse(BaseModel):
    job: JobResponse
    workflow: IngestionWorkflowResponse

