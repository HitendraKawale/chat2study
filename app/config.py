from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "chat2study"
    app_env: str = "dev"
    host: str = "127.0.0.1"
    port: int = 8000
    data_dir: Path = 
