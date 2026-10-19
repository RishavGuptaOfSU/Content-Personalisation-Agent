"""Conversation and message persistence."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.catalog import get_agent_spec
from app.core.logging import get_logger
from app.models.conversation import Conversation, Message
from app.models.feedback import Feedback

logger = get_logger(__name__)

_TITLE_CLEAN_RE = re.compile(r"\s+")


def derive_title(text: str, agent_key: str) -> str:
    """Produce a short, human title from the first user message."""
    cleaned = _TITLE_CLEAN_RE.sub(" ", (text or "").strip())
    if not cleaned:
        return get_agent_spec(agent_key).name
    cleaned = cleaned.lstrip("#*->• ").strip()
    if len(cleaned) <= 52:
        return cleaned
    truncated = cleaned[:52].rsplit(" ", 1)[0]
    return f"{truncated}…"


class ConversationService:
    # ------------------------------------------------------------- creation
    def create(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        agent_key: str,
        title: str | None = None,
        commit: bool = True,
    ) -> Conversation:
        spec = get_agent_spec(agent_key)
        conversation = Conversation(
            user_id=user_id,
            agent_key=spec.key,
            domain=spec.domain,
            title=title or "New conversation",
            message_count=0,
            is_archived=False,
            meta={},
        )
        db.add(conversation)
        if commit:
            db.commit()
            db.refresh(conversation)
        else:
            db.flush()
        return conversation

    def get(
        self, db: Session, *, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Conversation | None:
        return db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )

    def list(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        agent_key: str | None = None,
        domain: str | None = None,
        include_archived: bool = False,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
    ) -> list[Conversation]:
        statement = select(Conversation).where(Conversation.user_id == user_id)
        if agent_key:
            statement = statement.where(Conversation.agent_key == get_agent_spec(agent_key).key)
        if domain:
            statement = statement.where(Conversation.domain == domain)
        if not include_archived:
            statement = statement.where(Conversation.is_archived.is_(False))
        if search:
            statement = statement.where(Conversation.title.ilike(f"%{search.strip()}%"))
        statement = (
            statement.order_by(Conversation.updated_at.desc())
            .offset(max(offset, 0))
            .limit(min(limit, 200))
        )
        return list(db.scalars(statement).all())

    def rename(
        self, db: Session, *, conversation: Conversation, title: str
    ) -> Conversation:
        conversation.title = title.strip()[:255] or conversation.title
        db.commit()
        db.refresh(conversation)
        return conversation

    def set_archived(
        self, db: Session, *, conversation: Conversation, archived: bool
    ) -> Conversation:
        conversation.is_archived = archived
        db.commit()
        db.refresh(conversation)
        return conversation

    def delete(self, db: Session, *, conversation: Conversation) -> None:
        db.delete(conversation)
        db.commit()

    # ------------------------------------------------------------- messages
    def add_message(
        self,
        db: Session,
        *,
        conversation: Conversation,
        role: str,
        content: str,
        agent_key: str | None = None,
        output_kind: str = "text",
        media: list[dict[str, Any]] | None = None,
        meta: dict[str, Any] | None = None,
        commit: bool = False,
    ) -> Message:
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            agent_key=agent_key,
            output_kind=output_kind,
            media=media or [],
            meta=meta or {},
        )
        db.add(message)
        conversation.message_count = (conversation.message_count or 0) + 1
        conversation.updated_at = datetime.now(UTC)
        if commit:
            db.commit()
            db.refresh(message)
        else:
            db.flush()
        return message

    def list_messages(
        self, db: Session, *, conversation_id: uuid.UUID, limit: int = 500
    ) -> list[Message]:
        return list(
            db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .limit(limit)
            ).all()
        )

    def get_message(
        self, db: Session, *, user_id: uuid.UUID, message_id: uuid.UUID
    ) -> Message | None:
        return db.scalar(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Message.id == message_id, Conversation.user_id == user_id)
        )

    def feedback_ratings(
        self, db: Session, *, message_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """Latest rating per message, for rendering the feedback buttons."""
        if not message_ids:
            return {}
        rows = db.execute(
            select(Feedback.message_id, Feedback.rating, Feedback.created_at)
            .where(Feedback.message_id.in_(message_ids))
            .order_by(Feedback.created_at.asc())
        ).all()
        ratings: dict[uuid.UUID, int] = {}
        for message_id, rating, _created_at in rows:
            if message_id is not None:
                ratings[message_id] = int(rating)
        return ratings

    def last_message_preview(self, db: Session, conversation_id: uuid.UUID) -> str | None:
        content = db.scalar(
            select(Message.content)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        if not content:
            return None
        preview = _TITLE_CLEAN_RE.sub(" ", content.strip())
        return preview[:140]

    # ----------------------------------------------------------------- stats
    def counts_by_agent(self, db: Session, user_id: uuid.UUID) -> dict[str, dict[str, Any]]:
        rows = db.execute(
            select(
                Conversation.agent_key,
                func.count(Conversation.id),
                func.coalesce(func.sum(Conversation.message_count), 0),
                func.max(Conversation.updated_at),
            )
            .where(Conversation.user_id == user_id)
            .group_by(Conversation.agent_key)
        ).all()
        return {
            agent_key: {
                "conversations": int(conversations or 0),
                "messages": int(messages or 0),
                "last_used_at": last_used.isoformat() if last_used else None,
            }
            for agent_key, conversations, messages, last_used in rows
        }

    def totals(self, db: Session, user_id: uuid.UUID) -> tuple[int, int]:
        row = db.execute(
            select(
                func.count(Conversation.id),
                func.coalesce(func.sum(Conversation.message_count), 0),
            ).where(Conversation.user_id == user_id)
        ).one()
        return int(row[0] or 0), int(row[1] or 0)


_service: ConversationService | None = None


def get_conversation_service() -> ConversationService:
    global _service
    if _service is None:
        _service = ConversationService()
    return _service
