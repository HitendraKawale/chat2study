from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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


class IngestionWorkflowResponse(BaseModel):
    chat_id: str
    job_id: str
    title: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    source_domain: str | None = None
    selected_chat_provider: str | None = None
    selected_embedding_provider: str | None = None
    selected_chat_model: str | None = None
    selected_embedding_model: str | None = None
    capture_strategy: str | None = None
    planned_artifacts: list[str] = []
    complexity_score: int | None = None
    should_generate_notes: bool = False
    should_generate_visual_notes: bool = False


class IngestionRunResponse(BaseModel):
    job: JobResponse
    workflow: IngestionWorkflowResponse
