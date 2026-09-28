"""Conversation and message models, keyed by agent."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.database.types import JSONBType

if TYPE_CHECKING:  # pragma: no cover
    from app.models.feedback import Feedback
    from app.models.user import User


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A thread with one specific agent."""

    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    #: Fully qualified agent key, e.g. ``marketing.post-image``.
    agent_key: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    #: Denormalised domain for filtering history by domain.
    domain: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(255), default="New conversation", nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)

    user: Mapped[User] = relationship(back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Conversation {self.title!r} agent={self.agent_key}>"


class Message(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    #: "user" | "assistant" | "system"
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    #: Which agent produced/handled this message (assistant messages).
    agent_key: Mapped[str | None] = mapped_column(String(80), nullable=True)

    #: What this message carries: "text" | "image" | "chart".
    output_kind: Mapped[str] = mapped_column(String(16), default="text", nullable=False)
    #: Generated media (rendered images/charts) attached to this message.
    media: Mapped[list[dict[str, Any]]] = mapped_column(JSONBType, default=list, nullable=False)

    #: Routing decision, provider, token usage, personalization snapshot.
    meta: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
    feedback_entries: Mapped[list[Feedback]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )

    @property
    def has_media(self) -> bool:
        return bool(self.media)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Message {self.role} {self.output_kind} {self.content[:32]!r}>"
