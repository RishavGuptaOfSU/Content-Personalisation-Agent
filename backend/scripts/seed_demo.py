#!/usr/bin/env python
"""Seed a demo account so the app can be explored immediately.

Creates (idempotently):
  * a demo user — demo@example.com / DemoPass123
  * a global profile
  * **domain** profiles for education, technical, marketing and analytics
  * **agent** profiles for education.class10-maths, technical.python,
    marketing.social-copy and analytics.chart-builder
  * two conversations with real messages
  * long-term memories at all three scopes (agent / domain / global)

``marketing.post-image`` is deliberately left **unconfigured** so the
first-run agent setup flow can be demonstrated on a fresh login — its domain
profile exists, so the setup screen only asks the two image-specific questions.

    python scripts/seed_demo.py [--reset]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

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

#: domain key -> the shared answers every agent in that domain reuses
DOMAIN_PROFILES: dict[str, dict[str, object]] = {
    "education": {
        "board": "CBSE",
        "language": "English",
        "learning_style": ["Step-by-step working", "Practice questions"],
        "exam_target": "Class 10 board exam, March 2027",
    },
    "technical": {
        "experience": "3-5 years",
        "explanation_style": [
            "Runnable example first",
            "Type annotations",
            "Include a test",
        ],
        "project_context": "Multi-agent personalization platform on FastAPI + React",
    },
    "marketing": {
        "brand_name": "Acme Cloud",
        "industry": "SaaS / Software",
        "audience": ["Developers", "Founders"],
        "tone": "Professional",
        "brand_colors": "#4F46E5, #0F172A",
        "avoid": ["clickbait", "emojis"],
    },
    "analytics": {
        "experience": "Intermediate",
        "tools": ["Python / pandas", "SQL"],
        "domain_context": "B2B SaaS revenue and product usage data",
    },
}

#: agent key -> its own narrow answers
AGENT_PROFILES: dict[str, dict[str, object]] = {
    "education.class10-maths": {
        "weak_chapters": ["Trigonometry", "Circles", "Probability"],
        "detail_level": "Every single step",
    },
    "technical.python": {
        "python_version": "3.12",
        "frameworks": ["FastAPI", "SQLAlchemy", "pytest"],
        "level": "Advanced",
    },
    "marketing.social-copy": {
        "platforms": ["LinkedIn", "X / Twitter"],
        "length": "Short (50-120)",
        "use_hashtags": "Yes, a few",
    },
    "analytics.chart-builder": {
        "style": "Clean light",
        "default_chart": "Bar",
        "show_values": "Yes",
    },
}

#: (agent_key, domain, content, kind, importance) — None widens the scope
MEMORIES: list[tuple[str | None, str | None, str, str, float]] = [
    (None, None, "Prefers no emoji in any output", MemoryKind.PREFERENCE, 0.85),
    (
        "technical.python",
        "technical",
        "Prefers Python examples with type hints",
        MemoryKind.PREFERENCE,
        0.8,
    ),
    (
        None,
        "technical",
        "Works with FastAPI, React and PostgreSQL",
        MemoryKind.SKILL,
        0.7,
    ),
    (
        "education.class10-maths",
        "education",
        "Finds trigonometric identities the hardest part of the chapter",
        MemoryKind.REQUIREMENT,
        0.7,
    ),
    (
        "marketing.social-copy",
        "marketing",
        "Wants LinkedIn posts kept under 100 words",
        MemoryKind.PREFERENCE,
        0.75,
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
                "occupation": "Software engineer",
                "location": "Bengaluru, India",
                "language": "English",
                "preferred_response_length": "balanced",
                "communication_style": "direct",
                "general_skill_level": "intermediate",
                "interests": ["AI agents", "Cloud architecture", "Developer tooling"],
                "goals": ["Ship a SaaS side project", "Get better at system design"],
                "preferences": {"code_blocks": "always", "emoji": "never"},
                "bio": "Backend-leaning full-stack engineer building AI products.",
            },
        )
        print("  · global profile configured")

        # ----------------------------------------------------- domain profiles
        for domain, data in DOMAIN_PROFILES.items():
            profile = profiles.save_domain_profile(db, user.id, domain, data)
            print(f"  · domain profile {domain} (configured={profile.is_configured})")

        # ------------------------------------------------------ agent profiles
        for agent_key, data in AGENT_PROFILES.items():
            profile = profiles.save_agent_profile(db, user.id, agent_key, data)
            print(f"  · agent profile {agent_key} (configured={profile.is_configured})")
        print("  · marketing.post-image left UNCONFIGURED (first-run setup demo)")

        # -------------------------------------------------------- conversations
        has_conversations = db.scalar(
            select(Conversation).where(Conversation.user_id == user.id).limit(1)
        )
        if not has_conversations:
            technical = conversations.create(
                db,
                user_id=user.id,
                agent_key="technical.python",
                title="FastAPI dependency injection",
            )
            conversations.add_message(
                db,
                conversation=technical,
                role="user",
                content="How should I structure dependencies in FastAPI for a service layer?",
            )
            conversations.add_message(
                db,
                conversation=technical,
                role="assistant",
                agent_key="technical.python",
                content=(
                    "Keep the route thin: it should resolve dependencies and delegate.\n\n"
                    "Use `Annotated[Session, Depends(get_db)]` for the session, and put the "
                    "business logic behind a service object the route calls. That keeps the "
                    "service testable without FastAPI in the loop."
                ),
                meta={"provider": "seed", "model": "seed"},
            )
            maths = conversations.create(
                db,
                user_id=user.id,
                agent_key="education.class10-maths",
                title="Roots of a quadratic equation",
            )
            conversations.add_message(
                db,
                conversation=maths,
                role="user",
                content="Solve: find the roots of x² - 5x + 6 = 0",
            )
            conversations.add_message(
                db,
                conversation=maths,
                role="assistant",
                agent_key="education.class10-maths",
                content=(
                    "**Given** x² − 5x + 6 = 0\n\n"
                    "1. Factorise: find two numbers with product 6 and sum −5 → −2 and −3.\n"
                    "2. x² − 2x − 3x + 6 = 0\n"
                    "3. x(x − 2) − 3(x − 2) = 0\n"
                    "4. (x − 2)(x − 3) = 0\n\n"
                    "**Answer: x = 2 or x = 3**\n\n"
                    "*Common mistake:* writing the signs of the factors the wrong way round — "
                    "check by substituting both roots back in."
                ),
                meta={"provider": "seed", "model": "seed"},
            )
            db.commit()
            print("  · 2 seeded conversations with messages")
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
