"""Conversation history routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession, resolve_agent_key, resolve_domain_key
from app.schemas.chat import (
    ConversationCreate,
    ConversationDetail,
    ConversationRead,
    ConversationUpdate,
    MessageRead,
)
from app.services.conversation_service import get_conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _serialize(db, conversation) -> ConversationRead:  # type: ignore[no-untyped-def]
    payload = ConversationRead.model_validate(conversation)
    payload.last_message_preview = get_conversation_service().last_message_preview(
        db, conversation.id
    )
    return payload


@router.get("", response_model=list[ConversationRead])
def list_conversations(
    user: CurrentUser,
    db: DbSession,
    agent_key: str | None = Query(default=None, description="Filter by agent key"),
    domain: str | None = Query(default=None, description="Filter by domain"),
    include_archived: bool = Query(default=False),
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ConversationRead]:
    conversations = get_conversation_service().list(
        db,
        user_id=user.id,
        agent_key=resolve_agent_key(agent_key),
        domain=resolve_domain_key(domain),
        include_archived=include_archived,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [_serialize(db, conversation) for conversation in conversations]


@router.post("", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate, user: CurrentUser, db: DbSession
) -> ConversationRead:
    conversation = get_conversation_service().create(
        db,
        user_id=user.id,
        agent_key=resolve_agent_key(payload.agent_key),
        title=payload.title,
    )
    return _serialize(db, conversation)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> ConversationDetail:
    service = get_conversation_service()
    conversation = service.get(db, user_id=user.id, conversation_id=conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = service.list_messages(db, conversation_id=conversation.id)
    ratings = service.feedback_ratings(db, message_ids=[message.id for message in messages])

    detail = ConversationDetail.model_validate(conversation)
    detail.last_message_preview = service.last_message_preview(db, conversation.id)
    detail.messages = []
    for message in messages:
        item = MessageRead.model_validate(message)
        item.feedback_rating = ratings.get(message.id)
        detail.messages.append(item)
    return detail


@router.patch("/{conversation_id}", response_model=ConversationRead)
def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    user: CurrentUser,
    db: DbSession,
) -> ConversationRead:
    service = get_conversation_service()
    conversation = service.get(db, user_id=user.id, conversation_id=conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if payload.title is not None:
        conversation = service.rename(db, conversation=conversation, title=payload.title)
    if payload.is_archived is not None:
        conversation = service.set_archived(
            db, conversation=conversation, archived=payload.is_archived
        )
    return _serialize(db, conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: uuid.UUID, user: CurrentUser, db: DbSession) -> None:
    service = get_conversation_service()
    conversation = service.get(db, user_id=user.id, conversation_id=conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.delete(db, conversation=conversation)
