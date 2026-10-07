"""Provider registry — the single place a provider is chosen.

Switching the model backend is an environment change, never a code change:

    # Local models, no API key, no cloud
    LLM_PROVIDER=ollama
    OLLAMA_MODEL=llama3.2:3b
    EMBEDDING_PROVIDER=ollama

    # Any OpenAI-compatible API (OpenAI, Groq, Together, OpenRouter, LM Studio, vLLM)
    LLM_PROVIDER=openai
    OPENAI_BASE_URL=https://api.groq.com/openai/v1
    OPENAI_API_KEY=...

    # AWS Bedrock
    LLM_PROVIDER=bedrock

To add a new backend, implement ``BaseLLMProvider`` and register it in
``_LLM_FACTORIES``. No other module references a provider directly.
"""

from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import BaseEmbeddingProvider, BaseLLMProvider
from app.llm.embeddings import get_embedding_provider
from app.llm.local_provider import LocalDevLLMProvider

logger = get_logger(__name__)

_lock = Lock()
_llm_provider: BaseLLMProvider | None = None
_embedding_provider: BaseEmbeddingProvider | None = None


def _build_ollama() -> BaseLLMProvider:
    from app.llm.ollama import OllamaLLMProvider

    return OllamaLLMProvider()


def _build_openai() -> BaseLLMProvider:
    from app.llm.openai_compatible import OpenAICompatibleLLMProvider

    return OpenAICompatibleLLMProvider()


def _build_bedrock() -> BaseLLMProvider:
    from app.llm.bedrock import BedrockLLMProvider

    return BedrockLLMProvider()


_LLM_FACTORIES: dict[str, Callable[[], BaseLLMProvider]] = {
    "ollama": _build_ollama,
    "openai": _build_openai,
    "bedrock": _build_bedrock,
    "mock": LocalDevLLMProvider,
}


def get_llm_provider() -> BaseLLMProvider:
    """Return the process-wide LLM provider (lazily built, thread-safe)."""
    global _llm_provider
    if _llm_provider is None:
        with _lock:
            if _llm_provider is None:
                factory = _LLM_FACTORIES.get(settings.LLM_PROVIDER)
                if factory is None:
                    logger.error(
                        "Unknown LLM_PROVIDER=%r. Valid values: %s. "
                        "Falling back to the local development provider.",
                        settings.LLM_PROVIDER,
                        ", ".join(sorted(_LLM_FACTORIES)),
                    )
                    factory = LocalDevLLMProvider
                try:
                    _llm_provider = factory()
                except Exception as exc:  # pragma: no cover - misconfiguration path
                    logger.error(
                        "Failed to initialise LLM provider %r (%s); "
                        "falling back to the local development provider.",
                        settings.LLM_PROVIDER,
                        exc,
                    )
                    _llm_provider = LocalDevLLMProvider()
                logger.info(
                    "LLM provider: %s (%s)", _llm_provider.name, _llm_provider.default_model
                )
    return _llm_provider


def get_embeddings() -> BaseEmbeddingProvider:
    global _embedding_provider
    if _embedding_provider is None:
        with _lock:
            if _embedding_provider is None:
                _embedding_provider = get_embedding_provider()
                logger.info(
                    "Embedding provider: %s (dim=%d)",
                    _embedding_provider.name,
                    _embedding_provider.dimension,
                )
    return _embedding_provider


def reset_providers() -> None:
    """Testing hook."""
    global _llm_provider, _embedding_provider
    with _lock:
        _llm_provider = None
        _embedding_provider = None


def provider_status() -> dict[str, Any]:
    llm = get_llm_provider()
    embeddings = get_embeddings()

    embedding_info: dict[str, Any] = {
        "provider": embeddings.name,
        "dimension": embeddings.dimension,
        "configured_provider": settings.EMBEDDING_PROVIDER,
    }
    # Warn loudly when the column width does not match the model's real output.
    native = getattr(embeddings, "native_dimension", None)
    if native and native != embeddings.dimension:
        embedding_info["native_dimension"] = native
        embedding_info["warning"] = (
            f"Model emits {native} dims but EMBEDDING_DIM={embeddings.dimension}. "
            f"Set EMBEDDING_DIM={native} and re-run scripts/reembed_memories.py."
        )

    return {
        "llm": llm.health(),
        "configured_llm_provider": settings.LLM_PROVIDER,
        "embeddings": embedding_info,
        "router_model": settings.router_model or llm.default_model,
        "router_uses_llm": settings.ROUTER_USE_LLM and settings.uses_real_llm,
        "llm_memory_extraction": settings.MEMORY_LLM_EXTRACTION and settings.uses_real_llm,
    }
