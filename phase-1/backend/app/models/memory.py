"""Long-term semantic memory model (PostgreSQL + pgvector)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDPrimaryKeyMixin
from app.database.types import Embedding, JSONBType

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User


class MemoryKind:
    """Categories of durable memory (kept as plain strings for flexibility)."""

    PREFERENCE = "preference"
    INTEREST = "interest"
    REQUIREMENT = "requirement"
    FACT = "fact"
    FEEDBACK = "feedback"
    SKILL = "skill"

    ALL = (PREFERENCE, INTEREST, REQUIREMENT, FACT, FEEDBACK, SKILL)


class Memory(UUIDPrimaryKeyMixin, Base):
    """A single durable, retrievable fact/preference about the user.

    Only *useful* information is stored here — never a blind copy of every
    message. See ``app.memory.extractor``.
    """

    __tablename__ = "memories"
    __table_args__ = (
        Index("ix_memories_user_agent", "user_id", "agent_key"),
        Index("ix_memories_user_domain", "user_id", "domain"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    #: Scope widens as these are left unset: ``agent_key`` set -> that agent
    #: only; only ``domain`` set -> every agent in the domain; neither -> global.
    agent_key: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Embedding(), nullable=True)

    kind: Mapped[str] = mapped_column(String(32), default=MemoryKind.PREFERENCE, nullable=False)
    #: 0..1 — how strongly we trust this memory.
    importance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    #: How many times this memory has been observed/reinforced.
    occurrences: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    use_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    #: Provenance: source message id, conversation id, extraction reason, …
    meta: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)

    source_conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="memories")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Memory {self.kind} scope={self.agent_key or self.domain or 'global'}>"
