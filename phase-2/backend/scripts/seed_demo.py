#!/usr/bin/env python
"""Seed a demo account so the marketing agent can be explored immediately.

Creates (idempotently):
  * a demo user — demo@example.com / DemoPass123
  * a global profile
  * the **brand profile** (the Marketing domain profile)
  * agent profiles for social-copy, seo-optimizer and campaign-planner
  * one conversation with real messages
  * long-term memories at all three scopes (agent / domain / global)

``marketing.post-image`` and ``marketing.ad-creative`` are deliberately left
**unconfigured** so the first-run setup flow can be demonstrated — their brand
profile already exists, so setup only asks the agent-specific questions.

    python scripts/seed_demo.py [--reset]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.agents.definitions import PRIMARY_DOMAIN  # noqa: E402
from app.database.session import SessionLocal, init_db  # noqa: E402
from app.memory.extractor import MemoryCandidate  # noqa: E402
from app.memory.service import get_memory_service  # noqa: E402
from app.models import Conversation, Memory  # noqa: E402
from app.models.memory import MemoryKind  # noqa: E402
from app.services.conversation_service import get_conversation_service  # noqa: E402
from app.services.profile_service import get_profile_service  # noqa: E402
from app.services.user_service import EmailAlreadyRegistered, get_user_service  # noqa: E402

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "DemoPass123"
DEMO_NAME = "Demo User"

#: The brand profile — answered once, reused by all five agents.
BRAND_PROFILE: dict[str, object] = {
    "brand_name": "Acme Cloud",
    "industry": "SaaS / Software",
    "audience": ["Developers", "Founders"],
    "tone": "Professional",
    "brand_colors": "#4F46E5, #0F172A",
    "avoid": ["clickbait", "emojis"],
}

#: agent key -> its own narrow answers
AGENT_PROFILES: dict[str, dict[str, object]] = {
    "marketing.social-copy": {
        "platforms": ["LinkedIn", "X / Twitter"],
        "length": "Short (50-120)",
        "use_hashtags": "Yes, a few",
    },
    "marketing.seo-optimizer": {
        "content_type": "Landing page",
        "region": "India, English",
    },
    "marketing.campaign-planner": {
        "goal": "Lead generation",
        "channels": ["LinkedIn", "Email", "Blog / SEO"],
        "budget": "Small (<$500/mo)",
    },
}

#: (agent_key, domain, content, kind, importance) — None widens the scope
MEMORIES: list[tuple[str | None, str | None, str, str, float]] = [
    (None, None, "Prefers no emoji in any output", MemoryKind.PREFERENCE, 0.85),
    (
        None,
        PRIMARY_DOMAIN,
        "Positions Acme Cloud on engineering time saved, not on price",
        MemoryKind.REQUIREMENT,
        0.8,
    ),
    (
        "marketing.social-copy",
        PRIMARY_DOMAIN,
        "Wants LinkedIn posts kept under 100 words",
        MemoryKind.PREFERENCE,
        0.75,
    ),
    (
        "marketing.campaign-planner",
        PRIMARY_DOMAIN,
        "Reports campaign results to the founders every Monday",
        MemoryKind.FACT,
        0.6,
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed demo data")
    parser.add_argument(
        "--reset", action="store_true", help="Delete the demo user first, then re-seed"
    )
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    users = get_user_service()
    profiles = get_profile_service()
    conversations = get_conversation_service()
    memories = get_memory_service()

    try:
        existing = users.get_by_email(db, DEMO_EMAIL)
        if existing and args.reset:
            print(f"Removing existing demo user {DEMO_EMAIL}…")
            db.delete(existing)
            db.commit()
            existing = None

        if existing:
            print(f"Demo user already exists: {DEMO_EMAIL} (use --reset to recreate)")
            user = existing
        else:
            try:
                user = users.register(
                    db, name=DEMO_NAME, email=DEMO_EMAIL, password=DEMO_PASSWORD
                )
            except EmailAlreadyRegistered:
                user = users.get_by_email(db, DEMO_EMAIL)
                assert user is not None
            print(f"Created demo user {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # ----------------------------------------------------- global profile
        profiles.update_global_profile(
            db,
            user,
            {
                "display_name": "Demo User",
                "occupation": "Founder / marketer",
                "location": "Bengaluru, India",
                "language": "English",
                "preferred_response_length": "balanced",
                "communication_style": "direct",
                "general_skill_level": "intermediate",
                "interests": ["Developer marketing", "Positioning", "Content strategy"],
                "goals": ["Grow trial signups", "Publish consistently"],
                "preferences": {"emoji": "never"},
                "bio": "Marketing a developer-facing cloud cost tool.",
            },
        )
        print("  · global profile configured")

        # ------------------------------------------------------ brand profile
        brand = profiles.save_domain_profile(db, user.id, PRIMARY_DOMAIN, BRAND_PROFILE)
        print(f"  · brand profile ({PRIMARY_DOMAIN}) configured={brand.is_configured}")

        # ------------------------------------------------------ agent profiles
        for agent_key, data in AGENT_PROFILES.items():
            profile = profiles.save_agent_profile(db, user.id, agent_key, data)
            print(f"  · agent profile {agent_key} (configured={profile.is_configured})")
        print(
            "  · marketing.post-image and marketing.ad-creative left UNCONFIGURED "
            "(first-run setup demo)"
        )

        # -------------------------------------------------------- conversation
        has_conversations = db.scalar(
            select(Conversation).where(Conversation.user_id == user.id).limit(1)
        )
        if not has_conversations:
            thread = conversations.create(
                db,
                user_id=user.id,
                agent_key="marketing.social-copy",
                title="LinkedIn post on cloud waste",
            )
            conversations.add_message(
                db,
                conversation=thread,
                role="user",
                content="Write a LinkedIn post about how much cloud spend sits idle.",
            )
            conversations.add_message(
                db,
                conversation=thread,
                role="assistant",
                agent_key="marketing.social-copy",
                content=(
                    "Most teams are not overspending on cloud. They are paying for "
                    "capacity nobody remembers provisioning.\n\n"
                    "The fix is not a cheaper provider. It is knowing which "
                    "resources stopped earning their keep three sprints ago.\n\n"
                    "What is the oldest thing still running in your account?\n\n"
                    "#CloudCost #DevOps\n\n"
                    "**Why this works**\n"
                    "Opens with a reframe rather than a statistic, so there is nothing "
                    "to fact-check. One question as the only CTA."
                ),
                meta={"provider": "seed", "model": "seed"},
            )
            db.commit()
            print("  · 1 seeded conversation with messages")
        else:
            print("  · conversations already present, skipping")

        # ------------------------------------------------------------ memories
        existing_memories = db.scalar(select(Memory).where(Memory.user_id == user.id).limit(1))
        if not existing_memories:
            for agent_key, domain, content, kind, importance in MEMORIES:
                memories.remember(
                    db,
                    user_id=user.id,
                    candidate=MemoryCandidate(
                        content=content,
                        kind=kind,
                        importance=importance,
                        agent_scoped=agent_key is not None or domain is not None,
                        source="seed",
                        meta={"origin": "seed"},
                    ),
                    agent_key=agent_key,
                    domain=domain,
                )
            db.commit()
            print(f"  · {len(MEMORIES)} long-term memories with embeddings")
        else:
            print("  · memories already present, skipping")

        print("\nSeed complete.")
        print(f"  Login: {DEMO_EMAIL}  /  {DEMO_PASSWORD}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
