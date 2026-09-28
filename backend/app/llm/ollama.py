"""Ollama provider — local models with no API key and no cloud dependency.

Talks to the Ollama HTTP API directly (``/api/chat`` and ``/api/embed``) rather
than going through a client library, which keeps the dependency surface small
and the error messages actionable.

    LLM_PROVIDER=ollama
    OLLAMA_MODEL=llama3.2:3b
    EMBEDDING_PROVIDER=ollama
    OLLAMA_EMBEDDING_MODEL=nomic-embed-text
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import (
    BaseEmbeddingProvider,
    BaseLLMProvider,
    ChatMessage,
    LLMProviderError,
    LLMResponse,
)

logger = get_logger(__name__)


def _normalize_messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
    """Collapse consecutive same-role turns.

    Several open models (Gemma, Mistral) use chat templates that require strict
    user/assistant alternation and error out otherwise. The personalization
    engine can legitimately produce two user turns in a row (context block +
    request), so merge them before sending.
    """
    normalized: list[dict[str, str]] = []
    for message in messages:
        content = (message.content or "").strip()
        if not content:
            continue
        if normalized and normalized[-1]["role"] == message.role:
            normalized[-1]["content"] += f"\n\n{content}"
        else:
            normalized.append({"role": message.role, "content": content})
    return normalized


class OllamaLLMProvider(BaseLLMProvider):
    name = "ollama"

    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.OLLAMA_MODEL
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._timeout = settings.OLLAMA_TIMEOUT

    @property
    def default_model(self) -> str:
        return self._model

    # ------------------------------------------------------------------ chat
    def generate(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
        hints: dict[str, Any] | None = None,
    ) -> LLMResponse:
        model_id = model or self._model
        payload: dict[str, Any] = {
            "model": model_id,
            "stream": False,
            "keep_alive": settings.OLLAMA_KEEP_ALIVE,
            "messages": _normalize_messages(messages),
            "options": {
                "temperature": (
                    settings.LLM_TEMPERATURE if temperature is None else temperature
                ),
                "num_predict": max_tokens or settings.LLM_MAX_TOKENS,
                "num_ctx": settings.OLLAMA_NUM_CTX,
            },
        }
        if system:
            payload["messages"].insert(0, {"role": "system", "content": system})

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(f"{self._base_url}/api/chat", json=payload)
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                f"Ollama did not respond within {self._timeout}s. Local models are slow on "
                f"CPU — try a smaller OLLAMA_MODEL, lower LLM_MAX_TOKENS, or raise "
                f"OLLAMA_TIMEOUT."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(
                f"Cannot reach Ollama at {self._base_url}. Is `ollama serve` running? ({exc})"
            ) from exc

        if response.status_code == 404:
            raise LLMProviderError(
                f"Ollama has no model named {model_id!r}. Pull it first: `ollama pull {model_id}`"
            )
        if response.status_code >= 400:
            raise LLMProviderError(
                f"Ollama returned HTTP {response.status_code}: {response.text[:300]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMProviderError("Ollama returned a non-JSON response") from exc

        if "error" in data:
            raise LLMProviderError(f"Ollama error: {data['error']}")

        content = (data.get("message") or {}).get("content", "")
        if not str(content).strip():
            raise LLMProviderError(f"Ollama model {model_id!r} returned an empty response")

        return LLMResponse(
            content=str(content).strip(),
            model=model_id,
            provider=self.name,
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
            stop_reason=data.get("done_reason"),
            raw={
                "total_duration_ms": round((data.get("total_duration") or 0) / 1e6),
                "tokens_per_second": _tokens_per_second(data),
            },
        )

    # ---------------------------------------------------------------- stream
    supports_streaming = True

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
        hints: dict[str, Any] | None = None,
    ) -> Iterator[str]:
        """Yield tokens as Ollama produces them (NDJSON stream)."""
        model_id = model or self._model
        payload: dict[str, Any] = {
            "model": model_id,
            "stream": True,
            "keep_alive": settings.OLLAMA_KEEP_ALIVE,
            "messages": _normalize_messages(messages),
            "options": {
                "temperature": (
                    settings.LLM_TEMPERATURE if temperature is None else temperature
                ),
                "num_predict": max_tokens or settings.LLM_MAX_TOKENS,
                "num_ctx": settings.OLLAMA_NUM_CTX,
            },
        }
        if system:
            payload["messages"].insert(0, {"role": "system", "content": system})

        try:
            with httpx.Client(timeout=self._timeout) as client:
                with client.stream(
                    "POST", f"{self._base_url}/api/chat", json=payload
                ) as response:
                    if response.status_code == 404:
                        raise LLMProviderError(
                            f"Ollama has no model named {model_id!r}. "
                            f"Run: ollama pull {model_id}"
                        )
                    if response.status_code >= 400:
                        response.read()
                        raise LLMProviderError(
                            f"Ollama returned HTTP {response.status_code}: {response.text[:300]}"
                        )

                    for line in response.iter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except ValueError:
                            continue
                        if "error" in chunk:
                            raise LLMProviderError(f"Ollama error: {chunk['error']}")
                        piece = (chunk.get("message") or {}).get("content") or ""
                        if piece:
                            yield piece
                        if chunk.get("done"):
                            break
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                f"Ollama stopped responding after {self._timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(
                f"Cannot reach Ollama at {self._base_url}. Is `ollama serve` running? ({exc})"
            ) from exc

    # ---------------------------------------------------------------- health
    def health(self) -> dict[str, Any]:
        info: dict[str, Any] = {
            "provider": self.name,
            "model": self._model,
            "base_url": self._base_url,
            "supports_streaming": True,
        }
        try:
            with httpx.Client(timeout=5.0) as client:
                tags = client.get(f"{self._base_url}/api/tags")
            tags.raise_for_status()
            available = [m.get("name", "") for m in (tags.json().get("models") or [])]
            info["available_models"] = available
            # Ollama resolves a bare name to ":latest".
            wanted = self._model if ":" in self._model else f"{self._model}:latest"
            info["model_pulled"] = wanted in available or self._model in available
            info["ok"] = bool(info["model_pulled"])
            if not info["model_pulled"]:
                info["note"] = f"Model not pulled. Run: ollama pull {self._model}"
        except Exception as exc:
            info["ok"] = False
            info["note"] = f"Ollama unreachable at {self._base_url}: {exc}"
        return info


def _tokens_per_second(data: dict[str, Any]) -> float | None:
    eval_count = data.get("eval_count")
    eval_duration = data.get("eval_duration")
    if not eval_count or not eval_duration:
        return None
    return round(eval_count / (eval_duration / 1e9), 2)


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Real text embeddings from a local model (e.g. ``nomic-embed-text``)."""

    name = "ollama"

    #: Native output widths of the common Ollama embedding models.
    KNOWN_DIMENSIONS = {
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        "all-minilm": 384,
        "snowflake-arctic-embed": 1024,
        "bge-m3": 1024,
    }

    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.OLLAMA_EMBEDDING_MODEL
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._dimension = settings.EMBEDDING_DIM

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def native_dimension(self) -> int | None:
        base = self._model.split(":")[0]
        return self.KNOWN_DIMENSIONS.get(base)

    def _request(self, inputs: list[str]) -> list[list[float]]:
        try:
            with httpx.Client(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = client.post(
                    f"{self._base_url}/api/embed",
                    json={
                        "model": self._model,
                        "input": inputs,
                        "keep_alive": settings.OLLAMA_KEEP_ALIVE,
                    },
                )
        except httpx.HTTPError as exc:
            raise LLMProviderError(
                f"Cannot reach Ollama at {self._base_url} for embeddings ({exc})"
            ) from exc

        if response.status_code == 404:
            raise LLMProviderError(
                f"Ollama has no embedding model {self._model!r}. "
                f"Run: ollama pull {self._model}"
            )
        if response.status_code >= 400:
            raise LLMProviderError(
                f"Ollama embedding failed (HTTP {response.status_code}): {response.text[:200]}"
            )

        data = response.json()
        vectors = data.get("embeddings") or []
        if not vectors:
            raise LLMProviderError("Ollama returned no embeddings")
        return [[float(component) for component in vector] for vector in vectors]

    def embed(self, text: str) -> list[float]:
        vector = self._request([text or ""])[0]
        return self._fit(vector)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self._fit(vector) for vector in self._request([t or "" for t in texts])]

    def _fit(self, vector: list[float]) -> list[float]:
        """Pad/truncate to the configured column width.

        The vector column has a fixed width, so a provider whose native width
        differs from ``EMBEDDING_DIM`` would otherwise fail to insert. Padding
        with zeros preserves cosine similarity exactly; truncation does not, so
        it is logged loudly and the correct fix is to set ``EMBEDDING_DIM`` to
        the model's native width and re-embed.
        """
        size = len(vector)
        if size == self._dimension:
            return vector
        if size < self._dimension:
            return vector + [0.0] * (self._dimension - size)
        logger.warning(
            "Embedding model %s returned %d dims but EMBEDDING_DIM=%d; truncating. "
            "Set EMBEDDING_DIM=%d and re-embed (scripts/reembed_memories.py).",
            self._model,
            size,
            self._dimension,
            size,
        )
        return vector[: self._dimension]
