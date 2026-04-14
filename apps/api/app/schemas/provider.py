from typing import Any

from pydantic import BaseModel


class ProviderSummaryResponse(BaseModel):
    default_chat_provider: str
    default_embedding_provider: str
    supported_chat_providers: list[str]
    supported_embedding_providers: list[str]
    chat_models: dict[str, Any]
    embedding_models: dict[str, Any]
