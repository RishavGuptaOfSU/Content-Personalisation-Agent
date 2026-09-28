"""The ``process_feedback`` node, as its own compiled LangGraph.

Kept separate from the chat graph because it is triggered by a different event
(the user rating a message) while still being an explicit, inspectable node of
the overall pipeline described in the spec.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.conversation import Message
from app.services.feedback_service import FeedbackOutcome, get_feedback_service

logger = get_logger(__name__)


def _keep_last(_current: Any, incoming: Any) -> Any:
    return incoming


class FeedbackState(TypedDict):
    db: Annotated[Session, _keep_last]
    user_id: Annotated[uuid.UUID, _keep_last]
    message: Annotated[Message, _keep_last]
    rating: Annotated[int, _keep_last]
    feedback_text: Annotated[str | None, _keep_last]
    #: Written by the node; initialised to ``None`` (see ChatState note).
    outcome: Annotated[FeedbackOutcome | None, _keep_last]


def process_feedback(state: FeedbackState) -> dict[str, Any]:
    outcome = get_feedback_service().submit(
        state["db"],
        user_id=state["user_id"],
        message=state["message"],
        rating=state["rating"],
        feedback_text=state.get("feedback_text"),
    )
    logger.info(
        "Feedback processed: %d new memories, profile_changes=%s",
        len(outcome.memories_created),
        outcome.profile_changes or "none",
    )
    return {"outcome": outcome}


def build_feedback_graph() -> Any:
    graph = StateGraph(FeedbackState)
    graph.add_node("process_feedback", process_feedback)
    graph.add_edge(START, "process_feedback")
    graph.add_edge("process_feedback", END)
    return graph.compile()


_graph: Any | None = None


def get_feedback_graph() -> Any:
    global _graph
    if _graph is None:
        _graph = build_feedback_graph()
    return _graph


def run_feedback_pipeline(
    db: Session,
    *,
    user_id: uuid.UUID,
    message: Message,
    rating: int,
    feedback_text: str | None,
) -> FeedbackOutcome:
    state: FeedbackState = {
        "db": db,
        "user_id": user_id,
        "message": message,
        "rating": rating,
        "feedback_text": feedback_text,
        "outcome": None,
    }
    final = get_feedback_graph().invoke(state)
    return final["outcome"]
