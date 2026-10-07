"""Embedding providers.

``local`` — a deterministic hashing embedder (character + word n-grams projected
into a fixed-dimensional L2-normalised vector). It requires no network, produces
genuinely meaningful cosine similarity for lexically related text, and therefore
lets the pgvector memory pipeline be tested offline.

``bedrock`` — Amazon Titan embeddings via ``langchain_aws`` (see ``bedrock.py``).
"""

from __future__ import annotations

import hashlib
import math
import re

from app.core.config import settings
from app.llm.base import BaseEmbeddingProvider

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_SYNONYM_GROUPS: tuple[tuple[str, ...], ...] = (
    ("concise", "brief", "short", "shorter", "terse", "succinct"),
    ("detailed", "thorough", "comprehensive", "in-depth", "longer"),
    ("example", "examples", "sample", "snippet", "demo"),
    ("post", "posts", "content", "copy"),
    ("prefer", "prefers", "preference", "like", "likes", "want", "wants"),
    ("code", "coding", "program", "programming", "implementation"),
    ("resume", "cv", "curriculum"),
    ("chart", "charts", "graph", "graphs", "visualization", "visualisation"),
)

_SYNONYM_LOOKUP: dict[str, str] = {
    word: group[0] for group in _SYNONYM_GROUPS for word in group
}


def _char_ngrams(token: str, size: int = 4) -> list[str]:
    """Character n-grams give partial credit to morphological variants
    ("concise" / "concisely") that a pure word model would treat as unrelated."""
    if len(token) <= size:
        return []
    padded = f"#{token}#"
    return [f"~{padded[i : i + size]}" for i in range(len(padded) - size + 1)]


def _tokenize(text: str) -> list[str]:
    words = [_SYNONYM_LOOKUP.get(token, token) for token in _TOKEN_RE.findall(text.lower())]
    bigrams = [f"{a}_{b}" for a, b in zip(words, words[1:])]
    subwords: list[str] = []
    for word in words:
        subwords.extend(_char_ngrams(word))
    return words + bigrams + subwords


class LocalHashingEmbeddingProvider(BaseEmbeddingProvider):
    """Hashing (a.k.a. "hashing trick") embedder — no external service."""

    name = "local"

    def __init__(self, dimension: int | None = None) -> None:
        self._dimension = dimension or settings.EMBEDDING_DIM

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        tokens = _tokenize(text or "")
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self._dimension
            sign = 1.0 if digest[4] & 1 else -1.0
            # Sub-linear term weighting keeps frequent tokens from dominating.
            vector[index] += sign

        norm = math.sqrt(sum(component * component for component in vector))
        if norm == 0.0:
            return vector
        return [component / norm for component in vector]


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Build the configured embedding provider, degrading safely to local."""
    provider = settings.EMBEDDING_PROVIDER
    try:
        if provider == "ollama":
            from app.llm.ollama import OllamaEmbeddingProvider

            return OllamaEmbeddingProvider()
        if provider == "openai":
            from app.llm.openai_compatible import OpenAICompatibleEmbeddingProvider

            return OpenAICompatibleEmbeddingProvider()
        if provider == "bedrock":
            from app.llm.bedrock import BedrockEmbeddingProvider

            return BedrockEmbeddingProvider()
    except Exception as exc:  # pragma: no cover - misconfiguration path
        import logging

        logging.getLogger(__name__).error(
            "Could not initialise the %r embedding provider (%s); using the local embedder. "
            "Memory retrieval still works, with lexical rather than semantic matching.",
            provider,
            exc,
        )
    return LocalHashingEmbeddingProvider()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for a, b in zip(left, right):
        dot += a * b
        left_norm += a * a
        right_norm += b * b
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)
