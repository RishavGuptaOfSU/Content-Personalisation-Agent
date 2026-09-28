"""Chat, conversation, feedback and memory schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ------------------------------------------------------------------ chat
class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=16000)]
    conversation_id: uuid.UUID | None = None
    #: Explicit agent selection from the UI (``domain.slug``). Overrides the router.
    agent_key: str | None = None
    #: Optional plain-text attachment content (e.g. pasted CSV / uploaded txt).
    attachment_name: Annotated[str | None, Field(default=None, max_length=255)] = None
    attachment_text: Annotated[str | None, Field(default=None, max_length=40000)] = None

    @field_validator("message")
    @classmethod
    def _non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be empty")
        return value.strip()

    @field_validator("agent_key")
    @classmethod
    def _normalize_agent(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned or None


class RoutingInfo(BaseModel):
    agent_key: str
    domain: str
    agent_name: str
    source: Literal[
        "explicit", "keyword_router", "llm_router", "conversation_default", "fallback"
    ]
    confidence: float = 0.0
    reason: str = ""
    candidates: dict[str, float] = Field(default_factory=dict)


class ScopeInfo(BaseModel):
    """Whether the selected agent owns this request."""

    in_scope: bool
    reason: str = ""
    suggested_agent_key: str | None = None
    suggested_agent_name: str | None = None


class MediaRead(BaseModel):
    """A generated image or chart attached to a message."""

    filename: str
    url: str
    media_type: str
    mime_type: str
    width: int
    height: int
    bytes: int = 0
    alt_text: str = ""
    renderer: str = ""
    spec: dict[str, Any] = Field(default_factory=dict)


class MemoryUsed(BaseModel):
    id: uuid.UUID
    content: str
    kind: str
    scope: str = "global"
    similarity: float
    importance: float
    #: True when included as a standing preference rather than by topical recall.
    pinned: bool = False
    occurrences: int = 1


class PersonalizationTrace(BaseModel):
    """What the personalization engine fed to the model, surfaced in the UI so the
    user can see *why* a response looks the way it does."""

    agent_key: str
    domain: str
    output_kind: str = "text"
    global_profile_summary: list[str] = Field(default_factory=list)
    domain_profile_summary: list[str] = Field(default_factory=list)
    agent_profile_summary: list[str] = Field(default_factory=list)
    memories_used: list[MemoryUsed] = Field(default_factory=list)
    short_term_messages: int = 0
    context_characters: int = 0
    system_prompt_preview: str = ""
    provider: str = ""
    model: str = ""


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    agent_key: str | None = None
    output_kind: str = "text"
    media: list[MediaRead] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    feedback_rating: int | None = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    conversation_title: str
    user_message: MessageRead
    assistant_message: MessageRead
    routing: RoutingInfo
    scope: ScopeInfo
    personalization: PersonalizationTrace
    new_memories: list[str] = Field(default_factory=list)
    latency_ms: int = 0


# ---------------------------------------------------------- conversations
class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    agent_key: str
    domain: str
    title: str
    message_count: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    last_message_preview: str | None = None


class ConversationDetail(ConversationRead):
    messages: list[MessageRead] = Field(default_factory=list)


class ConversationCreate(BaseModel):
    agent_key: str
    title: Annotated[str | None, Field(default=None, max_length=255)] = None


class ConversationUpdate(BaseModel):
    title: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    is_archived: bool | None = None


# -------------------------------------------------------------- feedback
class FeedbackCreate(BaseModel):
    message_id: uuid.UUID
    rating: Annotated[int, Field(ge=-1, le=1)]
    feedback_text: Annotated[str | None, Field(default=None, max_length=2000)] = None

    @field_validator("rating")
    @classmethod
    def _non_zero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("rating must be 1 (helpful) or -1 (not helpful)")
        return value


class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    agent_key: str
    domain: str
    message_id: uuid.UUID | None
    rating: int
    feedback_text: str | None
    processed: bool
    outcome: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class FeedbackResult(BaseModel):
    feedback: FeedbackRead
    memories_created: list[str] = Field(default_factory=list)
    profile_updated: bool = False
    profile_changes: dict[str, Any] = Field(default_factory=dict)
    message: str = ""


# ---------------------------------------------------------------- memory
class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    agent_key: str | None
    domain: str | None
    content: str
    kind: str
    importance: float
    occurrences: int
    use_count: int
    is_active: bool
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_used_at: datetime | None = None


class MemoryCreate(BaseModel):
    content: Annotated[str, Field(min_length=3, max_length=1000)]
    #: Leave both unset for a global memory.
    agent_key: str | None = None
    domain: str | None = None
    kind: str = "preference"
    importance: Annotated[float, Field(ge=0.0, le=1.0)] = 0.6


class MemorySummary(BaseModel):
    total: int
    by_agent: dict[str, int] = Field(default_factory=dict)
    by_domain: dict[str, int] = Field(default_factory=dict)
    by_kind: dict[str, int] = Field(default_factory=dict)
    recent: list[MemoryRead] = Field(default_factory=list)


# ------------------------------------------------------------- dashboard
class DashboardStats(BaseModel):
    total_conversations: int
    total_messages: int
    total_memories: int
    configured_agents: int
    total_agents: int
    configured_domains: int
    total_domains: int
    images_generated: int = 0
    helpful_feedback: int
    unhelpful_feedback: int
