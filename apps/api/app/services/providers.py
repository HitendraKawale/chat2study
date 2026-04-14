from __future__ import annotations

from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings


class ProviderConfigError(ValueError):
    pass


def normalize_provider(value: str) -> str:
    provider = value.strip().lower()
    aliases = {
        "openai": "openai",
        "anthropic": "anthropic",
        "claude": "anthropic",
        "google": "google",
        "gemini": "google",
        "ollama": "ollama",
    }
    if provider not in aliases:
        raise ProviderConfigError(f"Unsupported provider: {value}")
    return aliases[provider]


def require_value(value: str | None, env_name: str) -> str:
    if value and value.strip():
        return value.strip()
    raise ProviderConfigError(f"Missing required configuration for {env_name}")


class ProviderFactory:
    @staticmethod
    def default_chat_provider() -> str:
        return normalize_provider(settings.default_chat_provider)

    @staticmethod
    def default_embedding_provider() -> str:
        return normalize_provider(settings.default_embedding_provider)

    @staticmethod
    def resolve_chat_model_name(provider: str | None = None) -> str:
        selected = normalize_provider(provider or settings.default_chat_provider)

        if selected == "openai":
            return require_value(settings.openai_chat_model, "OPENAI_CHAT_MODEL")
        if selected == "anthropic":
            return require_value(settings.anthropic_chat_model, "ANTHROPIC_CHAT_MODEL")
        if selected == "google":
            return require_value(settings.google_chat_model, "GOOGLE_CHAT_MODEL")
        if selected == "ollama":
            return require_value(settings.ollama_chat_model, "OLLAMA_CHAT_MODEL")

        raise ProviderConfigError(f"Unsupported chat provider: {selected}")

    @staticmethod
    def resolve_embedding_model_name(provider: str | None = None) -> str:
        selected = normalize_provider(provider or settings.default_embedding_provider)

        if selected == "openai":
            return require_value(
                settings.openai_embedding_model,
                "OPENAI_EMBEDDING_MODEL",
            )
        if selected == "google":
            return require_value(
                settings.google_embedding_model,
                "GOOGLE_EMBEDDING_MODEL",
            )
        if selected == "ollama":
            return require_value(
                settings.ollama_embedding_model,
                "OLLAMA_EMBEDDING_MODEL",
            )
        if selected == "anthropic":
            raise ProviderConfigError(
                "Anthropic chat models are supported, "
                "but embeddings are not configured in this project."
            )

        raise ProviderConfigError(f"Unsupported embedding provider: {selected}")

    @staticmethod
    def get_chat_model(provider: str | None = None) -> BaseChatModel:
        selected = normalize_provider(provider or settings.default_chat_provider)

        if selected == "openai":
            return ChatOpenAI(
                model=ProviderFactory.resolve_chat_model_name("openai"),
                temperature=0,
            )

        if selected == "anthropic":
            return ChatAnthropic(
                model=ProviderFactory.resolve_chat_model_name("anthropic"),
                temperature=0,
            )

        if selected == "google":
            return ChatGoogleGenerativeAI(
                model=ProviderFactory.resolve_chat_model_name("google"),
                temperature=0,
            )

        if selected == "ollama":
            return ChatOllama(
                model=ProviderFactory.resolve_chat_model_name("ollama"),
                base_url=settings.ollama_base_url,
                temperature=0,
            )

        raise ProviderConfigError(f"Unsupported chat provider: {selected}")

    @staticmethod
    def get_embedding_model(provider: str | None = None) -> Embeddings:
        selected = normalize_provider(provider or settings.default_embedding_provider)

        if selected == "openai":
            return OpenAIEmbeddings(model=ProviderFactory.resolve_embedding_model_name("openai"))

        if selected == "google":
            return GoogleGenerativeAIEmbeddings(
                model=ProviderFactory.resolve_embedding_model_name("google")
            )

        if selected == "ollama":
            return OllamaEmbeddings(
                model=ProviderFactory.resolve_embedding_model_name("ollama"),
                base_url=settings.ollama_base_url,
            )

        if selected == "anthropic":
            raise ProviderConfigError("Anthropic embeddings are not configured in this project.")

        raise ProviderConfigError(f"Unsupported embedding provider: {selected}")

    @staticmethod
    def summary() -> dict[str, Any]:
        return {
            "default_chat_provider": ProviderFactory.default_chat_provider(),
            "default_embedding_provider": ProviderFactory.default_embedding_provider(),
            "supported_chat_providers": ["ollama", "openai", "anthropic", "google"],
            "supported_embedding_providers": ["ollama", "openai", "google"],
            "chat_models": {
                "openai": settings.openai_chat_model,
                "anthropic": settings.anthropic_chat_model,
                "google": settings.google_chat_model,
                "ollama": settings.ollama_chat_model,
            },
            "embedding_models": {
                "openai": settings.openai_embedding_model,
                "google": settings.google_embedding_model,
                "ollama": settings.ollama_embedding_model,
            },
        }
