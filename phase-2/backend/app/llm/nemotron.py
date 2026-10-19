"""NVIDIA Nemotron provider.

Uses NVIDIA's OpenAI-compatible inference API:
    https://integrate.api.nvidia.com/v1

Supported models (set NEMOTRON_MODEL in .env):
    nvidia/llama-3.1-nemotron-70b-instruct   (default, best quality)
    nvidia/llama-3.1-nemotron-51b-instruct
    nvidia/nemotron-4-340b-instruct           (largest)
    nvidia/nemotron-mini-4b-instruct          (fastest, CPU-friendly)

Required env vars:
    LLM_PROVIDER=nemotron
    NVIDIA_API_KEY=nvapi-...     # from https://build.nvidia.com

Optional:
    NEMOTRON_MODEL=nvidia/llama-3.1-nemotron-70b-instruct
    NEMOTRON_ROUTER_MODEL=nvidia/nemotron-mini-4b-instruct
    NEMOTRON_BASE_URL=https://integrate.api.nvidia.com/v1
    NEMOTRON_TIMEOUT=180.0
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import (
    BaseLLMProvider,
    ChatMessage,
    LLMProviderError,
    LLMResponse,
)

logger = get_logger(__name__)

_DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
_DEFAULT_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct"
_DEFAULT_ROUTER_MODEL = "nvidia/nemotron-mini-4b-instruct"


class NemotronLLMProvider(BaseLLMProvider):
    """NVIDIA Nemotron via the NVIDIA Inference Microservices (NIM) API."""

    name = "nemotron"

    def __init__(self, model: str | None = None) -> None:
        self._model = model or getattr(settings, "NEMOTRON_MODEL", _DEFAULT_MODEL)
        self._base_url = getattr(
            settings, "NEMOTRON_BASE_URL", _DEFAULT_BASE_URL
        ).rstrip("/")
        self._timeout = float(getattr(settings, "NEMOTRON_TIMEOUT", 180.0))
        self._api_key = getattr(settings, "NVIDIA_API_KEY", None)
        if not self._api_key:
            raise LLMProviderError(
                "NVIDIA_API_KEY is not set. "
                "Get a free key at https://build.nvidia.com and add it to .env."
            )

    @property
    def default_model(self) -> str:
        return self._model

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

    def _build_payload(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
        model: str | None,
        stream: bool,
    ) -> dict[str, Any]:
        all_messages: list[dict[str, str]] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(m.to_dict() for m in messages)

        return {
            "model": model or self._model,
            "messages": all_messages,
            "temperature": settings.LLM_TEMPERATURE if temperature is None else temperature,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
            "stream": stream,
        }

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
        payload = self._build_payload(
            messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model_id,
            stream=False,
        )

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._headers(),
                )
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                f"NVIDIA API timed out after {self._timeout}s"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Cannot reach NVIDIA API ({exc})") from exc

        if response.status_code == 401:
            raise LLMProviderError(
                "NVIDIA API auth failed — check NVIDIA_API_KEY."
            )
        if response.status_code == 429:
            raise LLMProviderError("NVIDIA API rate limit hit. Retry shortly.")
        if response.status_code >= 400:
            raise LLMProviderError(
                f"NVIDIA API returned HTTP {response.status_code}: {response.text[:300]}"
            )

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise LLMProviderError("NVIDIA API returned no choices")

        content = (choices[0].get("message") or {}).get("content") or ""
        if not content.strip():
            raise LLMProviderError("NVIDIA API returned an empty message")

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
        """Yield token deltas from the SSE stream."""
        payload = self._build_payload(
            messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            stream=True,
        )

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
                            f"NVIDIA API HTTP {response.status_code}: {response.text[:300]}"
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
            raise LLMProviderError("NVIDIA API stream timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Cannot reach NVIDIA API ({exc})") from exc

    def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "model": self._model,
            "base_url": self._base_url,
            "api_key_configured": bool(self._api_key),
            "supports_streaming": True,
            "ok": True,
        }
