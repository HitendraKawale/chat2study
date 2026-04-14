from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SummaryCard(BaseModel):
    title: str
    body: str


class ConceptNode(BaseModel):
    id: str
    label: str
    kind: str = "concept"


class ConceptEdge(BaseModel):
    source: str
    target: str
    label: str | None = None


class VisualNotesDocument(BaseModel):
    title: str
    summary: str
    cards: list[SummaryCard] = Field(default_factory=list)
    nodes: list[ConceptNode] = Field(default_factory=list)
    edges: list[ConceptEdge] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)


class StudyNoteResponse(BaseModel):
    id: UUID
    chat_id: UUID
    note_type: str
    markdown: str
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime


class VisualNoteResponse(BaseModel):
    id: UUID
    chat_id: UUID
    note_type: str
    document: VisualNotesDocument
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime


class ChatNotesBundleResponse(BaseModel):
    study_notes: StudyNoteResponse | None = None
    visual_notes: VisualNoteResponse | None = None
