"""Decide what deserves to become a long-term memory.

Design rule from the spec: *do not store every message blindly*. A message only
produces a memory when it contains a durable signal — a stated preference, a
recurring interest, a hard requirement, or a correction delivered as feedback.

Two extractors:
  * ``RuleBasedExtractor`` — always available, deterministic, no model call.
  * ``LLMMemoryExtractor``  — used when a real LLM provider is configured; its
    output is validated and then merged with the rule-based candidates.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import ChatMessage, LLMProviderError
from app.llm.registry import get_llm_provider
from app.models.memory import MemoryKind

logger = get_logger(__name__)

_MAX_MEMORY_LENGTH = 240
_MIN_MEMORY_LENGTH = 8


@dataclass(slots=True)
class MemoryCandidate:
    content: str
    kind: str = MemoryKind.PREFERENCE
    importance: float = 0.55
    #: ``None`` => applies to every agent.
    agent_scoped: bool = True
    source: str = "rule"
    meta: dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> MemoryCandidate | None:
        content = " ".join(str(self.content).split())
        if len(content) < _MIN_MEMORY_LENGTH:
            return None
        if len(content) > _MAX_MEMORY_LENGTH:
            content = content[:_MAX_MEMORY_LENGTH].rsplit(" ", 1)[0] + "…"
        content = content[0].upper() + content[1:]
        kind = self.kind if self.kind in MemoryKind.ALL else MemoryKind.PREFERENCE
        importance = min(1.0, max(0.05, float(self.importance)))
        return MemoryCandidate(
            content=content,
            kind=kind,
            importance=importance,
            agent_scoped=self.agent_scoped,
            source=self.source,
            meta=dict(self.meta),
        )


# --------------------------------------------------------------------------
# Rule based extraction
# --------------------------------------------------------------------------
_PatternSpec = tuple[re.Pattern[str], str, float, str]

_PREFERENCE_PATTERNS: tuple[_PatternSpec, ...] = (
    (
        re.compile(r"\bi (?:prefer|like|love|enjoy)\s+(?P<value>[^.!?\n]{4,160})", re.I),
        MemoryKind.PREFERENCE,
        0.7,
        "Prefers {value}",
    ),
    (
        re.compile(
            r"\bi (?:don'?t|do not) (?:like|want|need)\s+(?P<value>[^.!?\n]{3,160})", re.I
        ),
        MemoryKind.PREFERENCE,
        0.7,
        "Does not want {value}",
    ),
    (
        re.compile(r"\b(?:please\s+)?(?:always|from now on)\s+(?P<value>[^.!?\n]{4,160})", re.I),
        MemoryKind.REQUIREMENT,
        0.8,
        "Standing instruction: {value}",
    ),
    (
        re.compile(r"\b(?:never|stop|avoid)\s+(?P<value>[^.!?\n]{3,160})", re.I),
        MemoryKind.REQUIREMENT,
        0.75,
        "Avoid {value}",
    ),
    (
        re.compile(
            r"\b(?:keep|make)\s+(?:it|them|this|these|answers?|responses?|posts?)\s+"
            r"(?P<value>short(?:er)?|concise|brief(?:er)?|detailed|longer|simpler|"
            r"more detailed|more concise)",
            re.I,
        ),
        MemoryKind.PREFERENCE,
        0.75,
        "Wants responses {value}",
    ),
    (
        re.compile(r"\bi(?:'m| am) (?:interested in|curious about)\s+(?P<value>[^.!?\n]{3,160})", re.I),
        MemoryKind.INTEREST,
        0.6,
        "Interested in {value}",
    ),
    (
        re.compile(
            r"\bi(?:'m| am) (?:learning|studying|preparing for)\s+(?P<value>[^.!?\n]{3,160})", re.I
        ),
        MemoryKind.INTEREST,
        0.65,
        "Currently learning {value}",
    ),
    (
        re.compile(r"\bi (?:work|code|build) (?:with|in|on)\s+(?P<value>[^.!?\n]{3,160})", re.I),
        MemoryKind.SKILL,
        0.6,
        "Works with {value}",
    ),
    (
        re.compile(r"\bi (?:use|am using)\s+(?P<value>[^.!?\n]{3,120})", re.I),
        MemoryKind.SKILL,
        0.55,
        "Uses {value}",
    ),
    (
        re.compile(r"\bmy (?:goal|target|aim) is\s+(?P<value>[^.!?\n]{3,160})", re.I),
        MemoryKind.REQUIREMENT,
        0.7,
        "Goal: {value}",
    ),
    (
        re.compile(
            r"\bi (?:must|need to|have to)\s+(?P<value>[^.!?\n]{4,160})", re.I
        ),
        MemoryKind.REQUIREMENT,
        0.6,
        "Needs to {value}",
    ),
    (
        re.compile(
            r"\b(?:my|our) (?:brand|company|product|team) is\s+(?P<value>[^.!?\n]{3,140})", re.I
        ),
        MemoryKind.FACT,
        0.65,
        "Brand/company context: {value}",
    ),
)

#: Feedback text is a stronger signal than a passing remark in a chat message.
_FEEDBACK_PATTERNS: tuple[_PatternSpec, ...] = (
    (
        re.compile(
            r"\b(?:make|keep)\s+(?:future\s+|next\s+)?(?P<target>[a-z ]{0,24}?)\s*"
            r"(?P<value>short(?:er)?|more concise|concise|brief(?:er)?|longer|"
            r"more detailed|detailed|simpler|more technical|less technical)",
            re.I,
        ),
        MemoryKind.PREFERENCE,
        0.85,
        "Wants {target} {value}",
    ),
    (
        re.compile(r"\b(?:too|very)\s+(?P<value>long|short|generic|basic|technical|verbose)", re.I),
        MemoryKind.PREFERENCE,
        0.7,
        "Found the response too {value} — adjust accordingly",
    ),
    (
        re.compile(r"\b(?:add|include)\s+(?:more\s+)?(?P<value>[^.!?\n]{3,120})", re.I),
        MemoryKind.PREFERENCE,
        0.7,
        "Wants more {value} included",
    ),
    (
        re.compile(r"\b(?:remove|drop|no more|without)\s+(?P<value>[^.!?\n]{3,120})", re.I),
        MemoryKind.PREFERENCE,
        0.7,
        "Wants {value} left out",
    ),
    (
        re.compile(r"\b(?:i|we) (?:prefer|want)\s+(?P<value>[^.!?\n]{3,160})", re.I),
        MemoryKind.PREFERENCE,
        0.8,
        "Prefers {value}",
    ),
)

_NOISE_PREFIXES = ("http://", "https://", "```")


def _apply_patterns(
    patterns: tuple[_PatternSpec, ...], text: str, source: str
) -> list[MemoryCandidate]:
    candidates: list[MemoryCandidate] = []
    for pattern, kind, importance, template in patterns:
        for match in pattern.finditer(text):
            groups = {key: (value or "").strip() for key, value in match.groupdict().items()}
            value = groups.get("value", "")
            if not value or value.lower().startswith(_NOISE_PREFIXES):
                continue
            value = value.rstrip(",;:").strip()
            rendered = template.format(**{**{"target": ""}, **groups})
            rendered = " ".join(rendered.split())
            candidate = MemoryCandidate(
                content=rendered,
                kind=kind,
                importance=importance,
                source=source,
                meta={"matched": match.group(0)[:120], "extractor": source},
            ).normalized()
            if candidate:
                candidates.append(candidate)
    return candidates


class RuleBasedExtractor:
    """Pattern based extraction — deterministic and dependency free."""

    name = "rule"

    def from_message(self, message: str) -> list[MemoryCandidate]:
        text = (message or "").strip()
        if len(text) < 12:
            return []
        # Ignore pure questions: they express a task, not a durable preference.
        if text.endswith("?") and len(text) < 120 and not re.search(r"\bi (prefer|like|use|am)\b", text, re.I):
            return []
        return _dedupe(_apply_patterns(_PREFERENCE_PATTERNS, text, self.name))

    def from_feedback(self, feedback_text: str, rating: int) -> list[MemoryCandidate]:
        text = (feedback_text or "").strip()
        if not text:
            return []
        candidates = _apply_patterns(_FEEDBACK_PATTERNS, text, "feedback")
        if not candidates and len(text) >= 15:
            # Keep an explicit correction even when no pattern matched, but at a
            # lower importance so it cannot dominate personalization on its own.
            sentiment = "liked" if rating > 0 else "asked to change"
            candidate = MemoryCandidate(
                content=f"Feedback ({sentiment}): {text}",
                kind=MemoryKind.FEEDBACK,
                importance=0.5 if rating > 0 else 0.6,
                source="feedback",
                meta={"extractor": "feedback-verbatim", "rating": rating},
            ).normalized()
            if candidate:
                candidates.append(candidate)
        for candidate in candidates:
            candidate.meta.setdefault("rating", rating)
        return _dedupe(candidates)


def _dedupe(candidates: list[MemoryCandidate]) -> list[MemoryCandidate]:
    seen: set[str] = set()
    unique: list[MemoryCandidate] = []
    for candidate in candidates:
        key = candidate.content.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique[:5]


# --------------------------------------------------------------------------
# LLM assisted extraction (used when a real provider is configured)
# --------------------------------------------------------------------------
_EXTRACTION_SYSTEM_PROMPT = """You extract durable user memories from a chat turn.

Return ONLY a JSON array. Each element:
{"content": "<third person statement about the user>",
 "kind": "preference|interest|requirement|fact|skill",
 "importance": <0.3-0.95>}

Rules:
- Only include information that will still be true next week.
- Never include the task itself, one-off questions, or anything about the assistant.
- Never include sensitive data (passwords, tokens, financial account numbers).
- Return [] when the turn contains nothing durable. Prefer [] over guessing.
- At most 3 items."""


class LLMMemoryExtractor:
    name = "llm"

    def extract(self, user_message: str, agent_key: str) -> list[MemoryCandidate]:
        provider = get_llm_provider()
        prompt = (
            f"Agent context: {agent_key}\n"
            f"User turn:\n\"\"\"\n{user_message[:4000]}\n\"\"\"\n\n"
            "JSON array:"
        )
        try:
            response = provider.generate(
                [ChatMessage(role="user", content=prompt)],
                system=_EXTRACTION_SYSTEM_PROMPT,
                temperature=0.0,
                max_tokens=400,
                hints={"task": "extract_memories", "request": user_message},
            )
        except LLMProviderError as exc:
            logger.warning("LLM memory extraction failed: %s", exc)
            return []

        return self._parse(response.content)

    @staticmethod
    def _parse(raw: str) -> list[MemoryCandidate]:
        match = re.search(r"\[.*]", raw or "", re.S)
        if not match:
            return []
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, list):
            return []

        candidates: list[MemoryCandidate] = []
        for item in payload[:3]:
            if not isinstance(item, dict):
                continue
            candidate = MemoryCandidate(
                content=str(item.get("content", "")),
                kind=str(item.get("kind", MemoryKind.PREFERENCE)).lower(),
                importance=float(item.get("importance", 0.6) or 0.6),
                source="llm",
                meta={"extractor": "llm"},
            ).normalized()
            if candidate:
                candidates.append(candidate)
        return candidates


class MemoryExtractor:
    """Facade combining the rule-based and (optional) LLM extractors."""

    def __init__(self) -> None:
        self._rules = RuleBasedExtractor()
        self._llm = LLMMemoryExtractor()

    @property
    def llm_enabled(self) -> bool:
        """Opt-in: it costs one extra model call per user message."""
        return settings.MEMORY_LLM_EXTRACTION and settings.uses_real_llm

    def from_message(self, message: str, agent_key: str) -> list[MemoryCandidate]:
        candidates = self._rules.from_message(message)
        if self.llm_enabled:
            candidates.extend(self._llm.extract(message, agent_key))
        return _dedupe(candidates)

    def from_feedback(self, feedback_text: str, rating: int) -> list[MemoryCandidate]:
        return self._rules.from_feedback(feedback_text, rating)


_extractor: MemoryExtractor | None = None


def get_memory_extractor() -> MemoryExtractor:
    global _extractor
    if _extractor is None:
        _extractor = MemoryExtractor()
    return _extractor
