from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


class ChatCreateRequest(BaseModel):
    url: AnyHttpUrl
    title: str | None = None
    source_type: str = "web_chat_url"


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID | None
    title: str
    status: str
    url: str
    source_type: str
    created_at: datetime
