from typing import Any, NotRequired, TypedDict


class IngestionState(TypedDict):
    chat_id: str
    job_id: str

    title: NotRequired[str]
    source_url: NotRequired[str]
    source_type: NotRequired[str]
    source_domain: NotRequired[str | None]

    selected_chat_provider: NotRequired[str]
    selected_embedding_provider: NotRequired[str]
    selected_chat_model: NotRequired[str]
    selected_embedding_model: NotRequired[str]

    planned_artifacts: NotRequired[list[str]]
    capture_strategy: NotRequired[str]

    complexity_score: NotRequired[int]
    should_generate_notes: NotRequired[bool]
    should_generate_visual_notes: NotRequired[bool]

    status: NotRequired[str]
    result_payload: NotRequired[dict[str, Any]]
    error: NotRequired[str]
