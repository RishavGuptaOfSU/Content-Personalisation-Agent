"""LLM + embedding provider interfaces.

Everything the application does with a model goes through these two protocols,
so swapping AWS Bedrock for another provider means adding one module and
changing ``LLM_PROVIDER`` in the environment — no call-site changes.
"""

from __future__ import annotations

import abc
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant"]


@dataclass(slots=True)
class ChatMessage:
    """One turn in a conversation, optionally carrying images.

    ``content`` stays a plain string in the overwhelming majority of cases.
    ``images`` holds ``data:image/...;base64,...`` URLs for a vision request;
    each provider renders them in its own wire format, because OpenAI wants a
    list of content parts and Ollama wants a sibling ``images`` field.
    """

    role: Role
    content: str
    images: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """OpenAI chat-completions shape, with image parts when present."""
        if not self.images:
            return {"role": self.role, "content": self.content}
        parts: list[dict[str, Any]] = []
        if self.content:
            parts.append({"type": "text", "text": self.content})
        parts.extend(
            {"type": "image_url", "image_url": {"url": url}} for url in self.images
        )
        return {"role": self.role, "content": parts}


@dataclass(slots=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    stop_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def usage(self) -> dict[str, int | None]:
        return {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens}


class LLMProviderError(RuntimeError):
    """Raised when the underlying model call fails."""


class BaseLLMProvider(abc.ABC):
    """A chat-completion provider."""

    name: str = "base"

    @abc.abstractmethod
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
        """Return a completion for ``messages``.

        ``hints`` carries the structured personalization payload. Real model
        providers ignore it (everything they need is already in the prompt); the
        local development provider uses it to compose a deterministic response
        without a network call.
        """

    @property
    @abc.abstractmethod
    def default_model(self) -> str: ...

    #: Set by providers that implement incremental generation.
    supports_streaming: bool = False

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
        """Yield the completion incrementally.

        The default implementation falls back to a single ``generate`` call and
        yields the whole result once, so every provider works with the streaming
        endpoint whether or not it supports real token streaming.
        """
        response = self.generate(
            messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            hints=hints,
        )
        yield response.content

    def health(self) -> dict[str, Any]:
        return {"provider": self.name, "model": self.default_model, "ok": True}


class BaseEmbeddingProvider(abc.ABC):
    """A text embedding provider used by the semantic memory store."""

    name: str = "base"

    @property
    @abc.abstractmethod
    def dimension(self) -> int: ...

    @abc.abstractmethod
    def embed(self, text: str) -> list[float]: ...

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
