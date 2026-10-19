"""Per-user views of the catalog: domain cards, agent cards, agent detail."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.catalog import (
    get_agent_spec,
    get_domain,
    list_agents,
    list_domains,
)
from app.models.memory import Memory
from app.services.conversation_service import get_conversation_service
from app.services.profile_service import get_profile_service


class CatalogService:
    def __init__(self) -> None:
        self._conversations = get_conversation_service()
        self._profiles = get_profile_service()

    # ---------------------------------------------------------------- counts
    def _memory_counts(self, db: Session, user_id: uuid.UUID) -> dict[str, int]:
        rows = db.execute(
            select(Memory.agent_key, Memory.domain, func.count(Memory.id))
            .where(Memory.user_id == user_id, Memory.is_active.is_(True))
            .group_by(Memory.agent_key, Memory.domain)
        ).all()
        counts: dict[str, int] = {}
        for agent_key, domain, count in rows:
            scope = agent_key or domain or "global"
            counts[scope] = counts.get(scope, 0) + int(count)
        return counts

    # --------------------------------------------------------------- domains
    def domains_for_user(self, db: Session, user_id: uuid.UUID) -> list[dict[str, Any]]:
        stats = self._conversations.counts_by_agent(db, user_id)
        agent_profiles = self._profiles.list_agent_profiles(db, user_id)
        domain_profiles = self._profiles.list_domain_profiles(db, user_id)
        memories = self._memory_counts(db, user_id)

        payload: list[dict[str, Any]] = []
        for domain in list_domains():
            agents = list_agents(domain.key)
            keys = [spec.key for spec in agents]
            conversations = sum(stats.get(key, {}).get("conversations", 0) for key in keys)
            messages = sum(stats.get(key, {}).get("messages", 0) for key in keys)
            configured = sum(
                1
                for key in keys
                if (profile := agent_profiles.get(key)) is not None and profile.is_configured
            )
            last_used = [
                stats[key]["last_used_at"] for key in keys if stats.get(key, {}).get("last_used_at")
            ]
            domain_profile = domain_profiles.get(domain.key)
            memory_count = memories.get(domain.key, 0) + sum(
                memories.get(key, 0) for key in keys
            )

            payload.append(
                {
                    **domain.to_dict(),
                    "agent_count": len(agents),
                    "configured_agents": configured,
                    "conversation_count": conversations,
                    "message_count": messages,
                    "memory_count": memory_count,
                    "domain_profile_configured": bool(
                        domain_profile and domain_profile.is_configured
                    ),
                    "status_label": (
                        "Personalized"
                        if domain_profile and domain_profile.is_configured
                        else "Not configured"
                    ),
                    "last_used_at": max(last_used) if last_used else None,
                    "visual_agents": [
                        spec.key for spec in agents if spec.output_kind.is_visual
                    ],
                }
            )
        return payload

    # ---------------------------------------------------------------- agents
    def agents_for_user(
        self, db: Session, user_id: uuid.UUID, domain_key: str | None = None
    ) -> list[dict[str, Any]]:
        stats = self._conversations.counts_by_agent(db, user_id)
        profiles = self._profiles.list_agent_profiles(db, user_id)
        memories = self._memory_counts(db, user_id)

        payload: list[dict[str, Any]] = []
        for spec in list_agents(domain_key):
            profile = profiles.get(spec.key)
            agent_stats = stats.get(spec.key, {})
            configured = bool(profile and profile.is_configured)
            payload.append(
                {
                    "key": spec.key,
                    "slug": spec.slug,
                    "domain": spec.domain,
                    "name": spec.name,
                    "tagline": spec.tagline,
                    "description": spec.description,
                    "icon": spec.icon,
                    "output_kind": spec.output_kind.value,
                    "scope": spec.scope,
                    "examples": list(spec.examples),
                    "conversation_count": agent_stats.get("conversations", 0),
                    "message_count": agent_stats.get("messages", 0),
                    "memory_count": memories.get(spec.key, 0),
                    "is_configured": configured,
                    "status_label": "Personalized" if configured else "Not configured",
                    "last_used_at": agent_stats.get("last_used_at"),
                }
            )
        return payload

    def agent_detail(
        self, db: Session, user_id: uuid.UUID, agent_key: str
    ) -> dict[str, Any]:
        spec = get_agent_spec(agent_key)
        domain = get_domain(spec.domain)
        status = self._profiles.agent_status(db, user_id, spec.key)
        agent_profile = self._profiles.get_agent_profile(db, user_id, spec.key)
        domain_profile = self._profiles.get_domain_profile(db, user_id, spec.domain)
        stats = self._conversations.counts_by_agent(db, user_id).get(spec.key, {})
        memories = self._memory_counts(db, user_id)

        payload = spec.to_dict()
        payload.update(
            {
                "domain_name": domain.name,
                "domain_accent": domain.accent,
                "domain_icon": domain.icon,
                "domain_setup_headline": domain.setup_headline,
                "domain_profile_fields": [f.to_dict() for f in domain.profile_fields],
                "domain_profile_data": domain_profile.profile_data if domain_profile else None,
                "profile_data": agent_profile.profile_data if agent_profile else None,
                "conversation_count": stats.get("conversations", 0),
                "message_count": stats.get("messages", 0),
                "memory_count": memories.get(spec.key, 0),
                "last_used_at": stats.get("last_used_at"),
                **status,
            }
        )
        return payload


_service: CatalogService | None = None


def get_catalog_service() -> CatalogService:
    global _service
    if _service is None:
        _service = CatalogService()
    return _service
