"""Feedback routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.agents.feedback_graph import run_feedback_pipeline
from app.api.deps import CurrentUser, DbSession, resolve_agent_key, resolve_domain_key
from app.core.http import HTTP_422_UNPROCESSABLE
from app.schemas.chat import FeedbackCreate, FeedbackRead, FeedbackResult
from app.services.conversation_service import get_conversation_service
from app.services.feedback_service import get_feedback_service

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResult, status_code=status.HTTP_201_CREATED)
def submit_feedback(payload: FeedbackCreate, user: CurrentUser, db: DbSession) -> FeedbackResult:
    """👍 / 👎 plus optional text. Runs the ``process_feedback`` graph node."""
    message = get_conversation_service().get_message(
        db, user_id=user.id, message_id=payload.message_id
    )
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if message.role != "assistant":
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE,
            detail="Feedback can only be given on assistant messages",
        )

    outcome = run_feedback_pipeline(
        db,
        user_id=user.id,
        message=message,
        rating=payload.rating,
        feedback_text=payload.feedback_text,
    )

    return FeedbackResult(
        feedback=FeedbackRead.model_validate(outcome.feedback),
        memories_created=outcome.memories_created,
        profile_updated=outcome.profile_updated,
        profile_changes=outcome.profile_changes,
        message=outcome.message,
    )


@router.get("", response_model=list[FeedbackRead])
def list_feedback(
    user: CurrentUser,
    db: DbSession,
    agent_key: str | None = Query(default=None),
    domain: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[FeedbackRead]:
    entries = get_feedback_service().list_for_user(
        db,
        user.id,
        agent_key=resolve_agent_key(agent_key),
        domain=resolve_domain_key(domain),
        limit=limit,
    )
    return [FeedbackRead.model_validate(entry) for entry in entries]
