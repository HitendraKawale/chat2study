from pydantic import BaseModel, Field


class SearchChunksRequest(BaseModel):
    query: str
    top_k: int | None = None


class AskChatRequest(BaseModel):
    question: str
    top_k: int | None = None


class RetrievedChunkResponse(BaseModel):
    chunk_id: str
    ordinal: int
    text: str
    token_count: int
    distance: float
    metadata_json: dict = Field(default_factory=dict)


class SearchChunksResponse(BaseModel):
    chat_id: str
    query: str
    top_k: int
    matches: list[RetrievedChunkResponse]


class AskChatResponse(BaseModel):
    chat_id: str
    question: str
    answer: str
    model_provider: str
    model_name: str
    matches: list[RetrievedChunkResponse]
