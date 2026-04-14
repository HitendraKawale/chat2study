from pydantic import BaseModel


class IndexChatResponse(BaseModel):
    chat_id: str
    status: str
    chunk_count: int
    embedding_provider: str
    embedding_model: str
    embedding_dimensions: int
