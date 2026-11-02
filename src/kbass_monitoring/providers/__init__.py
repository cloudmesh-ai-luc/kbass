"""LLM provider implementations and factory for CloudOps AI."""

from .base_provider import BaseLLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


_PROVIDERS = {
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str) -> BaseLLMProvider:
    """Return a configured LLM provider instance."""
    provider_class = _PROVIDERS.get(name.lower())

    if provider_class is None:
        raise ValueError(f"Unsupported AI provider: {name}")

    return provider_class()


def list_available_providers() -> list[str]:
    """Return supported AI provider names."""
    return list(_PROVIDERS)


__all__ = [
    "BaseLLMProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "get_provider",
    "list_available_providers",
]
