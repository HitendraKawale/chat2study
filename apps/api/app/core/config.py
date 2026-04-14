from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    project_name: str = Field(default="Chat2Study", alias="PROJECT_NAME")
    app_env: str = Field(default="development", alias="NODE_ENV")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    database_url: str = Field(
        default="postgresql+psycopg://chat2study:chat2study@localhost:5432/chat2study",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    s3_endpoint: str = Field(default="http://localhost:9000", alias="S3_ENDPOINT")
    s3_bucket: str = Field(default="chat2study", alias="S3_BUCKET")

    default_chat_provider: str = Field(default="ollama", alias="DEFAULT_CHAT_PROVIDER")
    default_embedding_provider: str = Field(
        default="ollama",
        alias="DEFAULT_EMBEDDING_PROVIDER",
    )
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    openai_chat_model: str | None = Field(default=None, alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str | None = Field(default=None, alias="OPENAI_EMBEDDING_MODEL")

    anthropic_chat_model: str | None = Field(default=None, alias="ANTHROPIC_CHAT_MODEL")

    google_chat_model: str | None = Field(default=None, alias="GOOGLE_CHAT_MODEL")
    google_embedding_model: str | None = Field(default=None, alias="GOOGLE_EMBEDDING_MODEL")

    ollama_chat_model: str = Field(default="llama3.2:3b", alias="OLLAMA_CHAT_MODEL")
    ollama_embedding_model: str = Field(
        default="nomic-embed-text",
        alias="OLLAMA_EMBEDDING_MODEL",
    )

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

