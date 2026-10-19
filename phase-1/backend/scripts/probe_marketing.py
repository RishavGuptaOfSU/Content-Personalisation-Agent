#!/usr/bin/env python
"""Read-only probe of the marketing agents' prompts, routing and scope.

Part of the Phase 2 audit. Builds the REAL personalized context for a marketing
request (no model call) and prints the exact system prompt each agent would
send, so prompt pollution and missing instructions are visible. Then scores a
set of marketing requests through the real router and scope guard.

Nothing is modified. Uses a throwaway SQLite database under /tmp.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/cpa_probe_marketing.db")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("EMBEDDING_PROVIDER", "local")

from app.agents.catalog import get_agent_spec, list_agents  # noqa: E402
from app.agents.router import get_router  # noqa: E402
from app.agents.runtime import get_agent  # noqa: E402
from app.agents.scope import assess  # noqa: E402
from app.agents.scoring import rank_agents, score_agent  # noqa: E402
from app.database.session import SessionLocal, init_db  # noqa: E402
from app.services.personalization import get_personalization_engine  # noqa: E402
from app.services.profile_service import get_profile_service  # noqa: E402
from app.services.user_service import get_user_service  # noqa: E402

DOMAIN_PROFILE = {
    "brand_name": "Acme Cloud",
    "industry": "SaaS / Software",
    "audience": ["Developers", "Founders"],
    "tone": "Professional",
    "brand_colors": "#4F46E5, #0F172A",
    "avoid": ["clickbait", "emojis"],
}
AGENT_PROFILES = {
    "marketing.post-image": {
        "platform": "LinkedIn",
        "style": "Bold type",
        "include_logo_text": "ACME CLOUD",
    },
    "marketing.ad-creative": {
        "objective": "Free trial signups",
        "size": "Landscape 1200x628",
    },
    "marketing.social-copy": {
        "platforms": ["LinkedIn"],
        "length": "Short (50-120)",
        "use_hashtags": "Yes, a few",
    },
    "marketing.seo-optimizer": {"content_type": "Blog post", "region": "India, English"},
    "marketing.campaign-planner": {
        "goal": "Lead generation",
        "channels": ["LinkedIn", "Email"],
        "budget": "Small (<$500/mo)",
    },
}

ROUTING_CASES = [
    ("Write an Instagram caption for our launch", "marketing.social-copy"),
    ("Create a LinkedIn post image about AI automation", "marketing.post-image"),
    ("Make a promotional graphic for our webinar", "marketing.post-image"),
    ("Design an ad creative for our free trial", "marketing.ad-creative"),
    ("Google display ad promoting 30% off annual plans", "marketing.ad-creative"),
    ("Title tag and meta description for our pricing page", "marketing.seo-optimizer"),
    ("Keyword research for a blog about DevOps", "marketing.seo-optimizer"),
    ("Plan a two week multi-channel launch campaign", "marketing.campaign-planner"),
    ("Build me a content calendar for next month", "marketing.campaign-planner"),
    # Deliberately ambiguous / overlapping — what happens?
    ("I need creative for our new product", None),
    ("Help me promote our webinar", None),
    ("Write ad copy for our free trial", None),
    ("Make something for LinkedIn", None),
]


def banner(text: str) -> None:
    print("\n" + "=" * 78)
    print(text)
    print("=" * 78)


def main() -> int:  # noqa: PLR0915
    init_db()
    db = SessionLocal()
    profiles = get_profile_service()
    try:
        email = f"probe+{uuid.uuid4().hex[:8]}@example.com"
        user = get_user_service().register(
            db, name="Probe User", email=email, password="ProbePass123"
        )
        profiles.save_domain_profile(db, user.id, "marketing", DOMAIN_PROFILE)
        for key, data in AGENT_PROFILES.items():
            profiles.save_agent_profile(db, user.id, key, data)
        db.commit()

        engine = get_personalization_engine()
        global_profile = profiles.get_or_create_global_profile(db, user)

        banner("1. ASSEMBLED SYSTEM PROMPT — marketing.post-image (an IMAGE agent)")
        spec = get_agent_spec("marketing.post-image")
        context = engine.build(
            db,
            user=user,
            agent_key=spec.key,
            request="Create a LinkedIn post image about cutting cloud costs",
            global_profile=global_profile,
            domain_profile=profiles.get_domain_profile(db, user.id, "marketing"),
            agent_profile=profiles.get_agent_profile(db, user.id, spec.key),
            conversation_id=None,
        )
        system_prompt, _ = get_agent(spec.key).build_prompt(context)
        print(system_prompt)

        banner("2. THE CONTEXT BLOCK SENT AS A USER MESSAGE (same request)")
        print(context.context_block)

        banner("3. PROSE DIRECTIVES REACHING THE IMAGE AGENTS")
        prose_markers = [
            "words", "preamble", "Second person", "jargon", "worked example",
            "paragraph", "exclamation", "hedge", "Contractions",
        ]
        for key in ("marketing.post-image", "marketing.ad-creative"):
            s = get_agent_spec(key)
            ctx = engine.build(
                db,
                user=user,
                agent_key=s.key,
                request="Create a graphic about cutting cloud costs",
                global_profile=global_profile,
                domain_profile=profiles.get_domain_profile(db, user.id, "marketing"),
                agent_profile=profiles.get_agent_profile(db, user.id, s.key),
                conversation_id=None,
            )
            prompt, _ = get_agent(s.key).build_prompt(ctx)
            hits = sorted({m for m in prose_markers if m.lower() in prompt.lower()})
            print(f"  {key:28s} prose markers present: {hits or 'none'}")
            print(f"  {'':28s} prompt length: {len(prompt)} chars")

        banner("4. ARE AGENT PROFILE FIELDS ACTUALLY NAMED IN THE INSTRUCTIONS?")
        for s in list_agents("marketing"):
            instr = s.instructions.lower()
            for f in s.profile_fields:
                label_hit = f.label.lower() in instr
                key_hit = f.key.replace("_", " ") in instr
                mark = "yes" if (label_hit or key_hit) else "NO"
                print(f"  {s.key:28s} {f.key:20s} referenced in instructions: {mark}")

        banner("5. MARKETING ROUTING (no explicit selection)")
        router = get_router()
        correct = wrong = ambiguous = 0
        for request, expected in ROUTING_CASES:
            decision = router.route(request)
            ranked = rank_agents(request, limit=3)
            runners = ", ".join(f"{r.agent_key.split('.')[-1]}={r.score:.1f}" for r in ranked)
            if expected is None:
                ambiguous += 1
                verdict = "ambiguous"
            elif decision.agent_key == expected:
                correct += 1
                verdict = "ok"
            else:
                wrong += 1
                verdict = f"WRONG (wanted {expected.split('.')[-1]})"
            in_marketing = decision.agent_key.startswith("marketing.")
            print(f"  {request[:52]:54s} -> {decision.agent_key.split('.')[-1]:18s}"
                  f"{'' if in_marketing else ' [LEFT MARKETING]'} {verdict}")
            print(f"  {'':54s}    scores: {runners or '(none)'}")
        print(f"\n  unambiguous cases: {correct} ok / {wrong} wrong; {ambiguous} ambiguous probes")

        banner("6. SCOPE GUARD BETWEEN MARKETING SIBLINGS")
        sibling_cases = [
            ("marketing.post-image", "Write me a LinkedIn caption about our launch"),
            ("marketing.social-copy", "Create the post image for our launch"),
            ("marketing.seo-optimizer", "Design an ad creative for the free trial"),
            ("marketing.campaign-planner", "Write the Instagram caption for day one"),
            ("marketing.post-image", "Plan a 6 week campaign across five channels"),
        ]
        for agent_key, request in sibling_cases:
            verdict = assess(request, agent_key)
            own = score_agent(request, get_agent_spec(agent_key)).score
            best = rank_agents(request, limit=1)
            best_txt = f"{best[0].agent_key.split('.')[-1]}={best[0].score:.1f}" if best else "-"
            status = (
                "in scope" if verdict.in_scope else f"HANDOFF -> {verdict.suggested_key}"
            )
            print(
                f"  {agent_key.split('.')[-1]:18s} <- {request[:44]:46s} "
                f"own={own:.1f} best={best_txt:22s} {status}"
            )

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
