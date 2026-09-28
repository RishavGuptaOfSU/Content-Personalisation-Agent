"""Dashboard aggregate stats."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.agents.catalog import DOMAIN_ORDER, agent_keys
from app.api.deps import CurrentUser, DbSession
from app.memory.service import get_memory_service
from app.models.conversation import Conversation, Message
from app.schemas.chat import DashboardStats
from app.services.conversation_service import get_conversation_service
from app.services.feedback_service import get_feedback_service
from app.services.profile_service import get_profile_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(user: CurrentUser, db: DbSession) -> DashboardStats:
    conversations, messages = get_conversation_service().totals(db, user.id)
    memory_stats = get_memory_service().summary(db, user_id=user.id)
    service = get_profile_service()
    agent_profiles = service.list_agent_profiles(db, user.id)
    domain_profiles = service.list_domain_profiles(db, user.id)
    helpful, unhelpful = get_feedback_service().counts(db, user.id)

    images = db.scalar(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.user_id == user.id,
            Message.output_kind.in_(("image", "chart")),
        )
    ) or 0

    return DashboardStats(
        total_conversations=conversations,
        total_messages=messages,
        total_memories=memory_stats["total"],
        configured_agents=sum(1 for p in agent_profiles.values() if p.is_configured),
        total_agents=len(agent_keys()),
        configured_domains=sum(1 for p in domain_profiles.values() if p.is_configured),
        total_domains=len(DOMAIN_ORDER),
        images_generated=int(images),
        helpful_feedback=helpful,
        unhelpful_feedback=unhelpful,
    )
