"""Feedback model — the signal that drives profile/memory adaptation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDPrimaryKeyMixin
from app.database.types import JSONBType

if TYPE_CHECKING:  # pragma: no cover
    from app.models.conversation import Message
    from app.models.user import User


class Feedback(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    agent_key: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), index=True, nullable=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )

    #: +1 (helpful) or -1 (not helpful)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    #: Set once the feedback has been folded into memory/profile.
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    #: What the system did with it (memory ids created, profile keys changed).
    outcome: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    user: Mapped[User] = relationship(back_populates="feedback_entries")
    message: Mapped[Message | None] = relationship(back_populates="feedback_entries")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Feedback {self.rating:+d} {self.agent_key}>"
