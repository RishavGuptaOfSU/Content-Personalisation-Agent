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
        budget = max_tokens or settings.LLM_MAX_TOKENS
        attempted: list[int] = []

        while True:
            attempted.append(budget)
            data = self._post_chat(
                model_id=model_id,
                messages=messages,
                system=system,
                temperature=temperature,
                max_tokens=budget,
            )
            choices = data.get("choices") or []
            if not choices:
                raise LLMProviderError("Provider returned no choices")
            message = choices[0].get("message") or {}
            content = (message.get("content") or "").strip()
            finish_reason = choices[0].get("finish_reason")
            if content:
                break

            retry_budget = self._headroom(budget)
            if not self._is_exhausted_by_reasoning(finish_reason, message) or retry_budget is None:
                raise LLMProviderError(
                    self._empty_reply_message(model_id, finish_reason, message, attempted)
                )
            logger.warning(
                "%s returned an empty message with finish_reason=%r at max_tokens=%d; "
                "the token budget went on hidden reasoning. Retrying at %d.",
                model_id,
                finish_reason,
                budget,
                retry_budget,
            )
            budget = retry_budget

        usage = data.get("usage") or {}
        return LLMResponse(
            content=content,
            model=data.get("model", model_id),
            provider=self.name,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            stop_reason=finish_reason,
            raw={"id": data.get("id"), "token_budgets": attempted},
        )

    # ------------------------------------------------------------- internals
    def _post_chat(
        self,
        *,
        model_id: str,
        messages: list[ChatMessage],
        system: str | None,
        temperature: float | None,
        max_tokens: int,
    ) -> dict[str, Any]:
        """One non-streaming chat call, with provider errors normalised."""
        payload: dict[str, Any] = {
            "model": model_id,
            "temperature": settings.LLM_TEMPERATURE if temperature is None else temperature,
            "max_tokens": max_tokens,
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
        return response.json()

    def _headroom(self, budget: int) -> int | None:
        """A larger budget to retry with, or None when there is none to give."""
        if not settings.LLM_EMPTY_REPLY_RETRY:
            return None
        ceiling = max(settings.LLM_MAX_TOKENS_CEILING, 0)
        if budget >= ceiling:
            return None
        larger = int(budget * max(settings.LLM_EMPTY_REPLY_BUDGET_MULTIPLIER, 1.0))
        return min(larger, ceiling) if larger > budget else None

    @staticmethod
    def _is_exhausted_by_reasoning(finish_reason: str | None, message: dict[str, Any]) -> bool:
        """True when an empty reply is a spent token budget, not a broken model.

        Two signatures count. ``finish_reason == "length"`` is the API saying it
        stopped because the cap was hit. A populated ``reasoning`` field with no
        ``content`` is the model saying it only ever got as far as thinking.
        """
        if finish_reason == "length":
            return True
        reasoning = message.get("reasoning") or message.get("reasoning_content") or ""
        return bool(str(reasoning).strip())

    @staticmethod
    def _empty_reply_message(
        model_id: str,
        finish_reason: str | None,
        message: dict[str, Any],
        attempted: list[int],
    ) -> str:
        reasoning = str(message.get("reasoning") or message.get("reasoning_content") or "")
        detail = (
            f"{model_id} returned an empty message (finish_reason="
            f"{finish_reason!r}) at max_tokens={attempted}"
        )
        if reasoning.strip():
            detail += (
                f"; it produced {len(reasoning)} characters of hidden reasoning and no "
                "answer, so the whole budget went on thinking. Raise LLM_MAX_TOKENS "
                "or LLM_MAX_TOKENS_CEILING, or use a non-reasoning model"
            )
        return detail

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
        """Yield deltas from the SSE stream.

        A reasoning model can stream nothing but hidden thinking and then stop,
        which would leave the caller with a silently empty reply. If no visible
        delta arrived, this falls back to ``generate()``, which has the
        budget-headroom retry, and yields that answer instead.
        """
        model_id = model or self._model
        budget = max_tokens or settings.LLM_MAX_TOKENS
        payload: dict[str, Any] = {
            "model": model_id,
            "temperature": settings.LLM_TEMPERATURE if temperature is None else temperature,
            "max_tokens": budget,
            "stream": True,
            "messages": (
                ([{"role": "system", "content": system}] if system else [])
                + [message.to_dict() for message in messages]
            ),
        }

        yielded_any = False
        finish_reason: str | None = None
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
                        finish_reason = choices[0].get("finish_reason") or finish_reason
                        piece = (choices[0].get("delta") or {}).get("content") or ""
                        if piece:
                            yielded_any = True
                            yield piece
        except httpx.TimeoutException as exc:
            raise LLMProviderError(f"{self._base_url} timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Cannot reach {self._base_url} ({exc})") from exc

        if not yielded_any:
            logger.warning(
                "%s streamed no visible content (finish_reason=%r); retrying "
                "without streaming so the budget-headroom path can run.",
                model_id,
                finish_reason,
            )
            response = self.generate(
                messages,
                system=system,
                temperature=temperature,
                max_tokens=self._headroom(budget) or budget,
                model=model_id,
            )
            yield response.content

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
