"""OpenAI-compatible provider.

One implementation covers every service that speaks the OpenAI Chat Completions
API, which is most of them:

| Service      | ``OPENAI_BASE_URL``                        |
|--------------|--------------------------------------------|
| OpenAI       | ``https://api.openai.com/v1``              |
| Groq         | ``https://api.groq.com/openai/v1``         |
| Together AI  | ``https://api.together.xyz/v1``            |
| OpenRouter   | ``https://openrouter.ai/api/v1``           |
| Mistral      | ``https://api.mistral.ai/v1``              |
| LM Studio    | ``http://localhost:1234/v1``               |
| vLLM         | ``http://localhost:8001/v1``               |
| Ollama       | ``http://localhost:11434/v1`` (native provider preferred) |

    LLM_PROVIDER=openai
    OPENAI_BASE_URL=https://api.groq.com/openai/v1
    OPENAI_API_KEY=...
    OPENAI_MODEL=llama-3.3-70b-versatile
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


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.OPENAI_MODEL
        self._base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self._timeout = settings.OPENAI_TIMEOUT

    @property
    def default_model(self) -> str:
        return self._model

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.OPENAI_API_KEY:
            headers["Authorization"] = f"Bearer {settings.OPENAI_API_KEY}"
        return headers

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
            "temperature": settings.LLM_TEMPERATURE if temperature is None else temperature,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
            "stream": False,
            "messages": (
                ([{"role": "system", "content": system}] if system else [])
                + [message.to_dict() for message in messages]
            ),
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._headers(),
                )
        except httpx.TimeoutException as exc:
            raise LLMProviderError(f"{self._base_url} timed out after {self._timeout}s") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Cannot reach {self._base_url} ({exc})") from exc

        if response.status_code == 401:
            raise LLMProviderError("Authentication failed — check OPENAI_API_KEY.")
        if response.status_code == 429:
            raise LLMProviderError("Rate limited by the provider. Retry shortly.")
        if response.status_code >= 400:
            raise LLMProviderError(
                f"Provider returned HTTP {response.status_code}: {response.text[:300]}"
            )

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise LLMProviderError("Provider returned no choices")
        content = (choices[0].get("message") or {}).get("content") or ""
        if not content.strip():
            raise LLMProviderError("Provider returned an empty message")

        usage = data.get("usage") or {}
        return LLMResponse(
            content=content.strip(),
            model=data.get("model", model_id),
            provider=self.name,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            stop_reason=choices[0].get("finish_reason"),
            raw={"id": data.get("id")},
        )

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
        """Yield deltas from the SSE stream."""
        model_id = model or self._model
        payload: dict[str, Any] = {
            "model": model_id,
            "temperature": settings.LLM_TEMPERATURE if temperature is None else temperature,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
            "stream": True,
            "messages": (
                ([{"role": "system", "content": system}] if system else [])
                + [message.to_dict() for message in messages]
            ),
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                with client.stream(
                    "POST",
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._headers(),
                ) as response:
                    if response.status_code >= 400:
                        response.read()
                        raise LLMProviderError(
                            f"Provider returned HTTP {response.status_code}: "
                            f"{response.text[:300]}"
                        )
                    for line in response.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                        except ValueError:
                            continue
                        choices = chunk.get("choices") or []
                        if not choices:
                            continue
                        piece = (choices[0].get("delta") or {}).get("content") or ""
                        if piece:
                            yield piece
        except httpx.TimeoutException as exc:
            raise LLMProviderError(f"{self._base_url} timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Cannot reach {self._base_url} ({exc})") from exc

    def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "model": self._model,
            "base_url": self._base_url,
            "api_key_configured": bool(settings.OPENAI_API_KEY),
            "supports_streaming": True,
            "ok": True,
        }


class OpenAICompatibleEmbeddingProvider(BaseEmbeddingProvider):
    name = "openai"

    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.OPENAI_EMBEDDING_MODEL
        self._base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self._dimension = settings.EMBEDDING_DIM

    @property
    def dimension(self) -> int:
        return self._dimension

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.OPENAI_API_KEY:
            headers["Authorization"] = f"Bearer {settings.OPENAI_API_KEY}"
        return headers

    def _request(self, inputs: list[str]) -> list[list[float]]:
        payload: dict[str, Any] = {"model": self._model, "input": inputs}
        # OpenAI's v3 embedding models support native dimension reduction.
        if self._model.startswith("text-embedding-3"):
            payload["dimensions"] = self._dimension

        try:
            with httpx.Client(timeout=settings.OPENAI_TIMEOUT) as client:
                response = client.post(
                    f"{self._base_url}/embeddings", json=payload, headers=self._headers()
                )
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Embedding request failed ({exc})") from exc

        if response.status_code >= 400:
            raise LLMProviderError(
                f"Embedding failed (HTTP {response.status_code}): {response.text[:200]}"
            )

        items = response.json().get("data") or []
        if not items:
            raise LLMProviderError("Provider returned no embeddings")
        return [[float(c) for c in item["embedding"]] for item in items]

    def embed(self, text: str) -> list[float]:
        return self._fit(self._request([text or ""])[0])

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self._fit(vector) for vector in self._request([t or "" for t in texts])]

    def _fit(self, vector: list[float]) -> list[float]:
        if len(vector) == self._dimension:
            return vector
        if len(vector) < self._dimension:
            return vector + [0.0] * (self._dimension - len(vector))
        logger.warning(
            "Embedding model returned %d dims, EMBEDDING_DIM=%d; truncating.",
            len(vector),
            self._dimension,
        )
        return vector[: self._dimension]
