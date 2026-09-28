#!/usr/bin/env python
"""Report exactly what the personalization engine sends to the model.

Prompt evaluation dominates latency on CPU-only hardware (measured here:
~16 tokens/sec in, ~5 tokens/sec out), so a short user message can still be slow
if the assembled prompt is large. This prints the breakdown — scope contract,
task instructions, three profile levels, memories, history — so the cost is
visible without waiting for a generation.

    python scripts/measure_prompt.py "hi"
    python scripts/measure_prompt.py "Solve x^2-5x+6=0" --agent education.class10-maths
    python scripts/measure_prompt.py "hi" --agent technical.python --conversation <id>
    python scripts/measure_prompt.py --all          # every agent, one row each
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.agents.catalog import get_agent_spec, list_agents  # noqa: E402
from app.agents.runtime import get_agent  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models import Conversation, User  # noqa: E402
from app.services.personalization import get_personalization_engine  # noqa: E402
from app.services.profile_service import get_profile_service  # noqa: E402

# Measured on this machine with llama3.2:3b on CPU (no GPU).
PROMPT_TOKENS_PER_SEC = 16.0
OUTPUT_TOKENS_PER_SEC = 5.5


def build_context(db, user, agent_key: str, message: str, conversation_id=None):
    profiles = get_profile_service()
    spec = get_agent_spec(agent_key)
    return get_personalization_engine().build(
        db,
        user=user,
        agent_key=spec.key,
        request=message,
        global_profile=profiles.get_or_create_global_profile(db, user),
        domain_profile=profiles.get_domain_profile(db, user.id, spec.domain),
        agent_profile=profiles.get_agent_profile(db, user.id, spec.key),
        conversation_id=conversation_id,
    )


def main() -> int:  # noqa: PLR0915 - a linear report
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", default="hi")
    parser.add_argument(
        "--agent",
        default="technical.python",
        help="Agent key, e.g. education.class10-maths",
    )
    parser.add_argument(
        "--conversation", default=None, help="Conversation id (longest for this agent if omitted)"
    )
    parser.add_argument("--email", default=None)
    parser.add_argument(
        "--all", action="store_true", help="One summary row per agent instead of a breakdown"
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.email:
            user = db.scalar(select(User).where(User.email == args.email.lower()))
        else:
            user = db.scalars(select(User)).first()
        if user is None:
            print("No users in the database. Run scripts/seed_demo.py first.")
            return 1

        if args.all:
            print(f"user: {user.email}   message: {args.message!r}\n")
            print(f"{'agent':<30}{'kind':<7}{'prompt':>8}{'ctx':>8}{'~tok':>7}{'est s':>8}")
            print("-" * 68)
            for spec in list_agents():
                context = build_context(db, user, spec.key, args.message)
                system_prompt, _ = get_agent(spec.key).build_prompt(context)
                total = (
                    len(system_prompt)
                    + len(context.context_block)
                    + sum(len(m.content) for m in context.short_term)
                    + len(context.user_request)
                )
                tokens = total / 4
                print(
                    f"{spec.key:<30}{spec.output_kind.value:<7}"
                    f"{len(system_prompt):>8}{len(context.context_block):>8}"
                    f"{int(tokens):>7}{tokens / PROMPT_TOKENS_PER_SEC:>8.1f}"
                )
            return 0

        spec = get_agent_spec(args.agent)

        conversation = None
        if args.conversation:
            try:
                conversation = db.get(Conversation, uuid.UUID(args.conversation))
            except ValueError:
                print(f"Not a valid conversation id: {args.conversation!r}")
                return 1
        if conversation is None:
            conversation = db.scalars(
                select(Conversation)
                .where(Conversation.agent_key == spec.key)
                .order_by(Conversation.message_count.desc())
                .limit(1)
            ).first()
        if conversation is not None:
            user = db.get(User, conversation.user_id) or user

        context = build_context(
            db,
            user,
            spec.key,
            args.message,
            conversation_id=conversation.id if conversation else None,
        )
        agent = get_agent(spec.key)
        system_prompt, _ = agent.build_prompt(context)

        print(f"user            : {user.email}")
        print(f"agent           : {spec.key}  ({spec.name}, output={spec.output_kind.value})")
        print(f"domain          : {spec.domain}")
        print(f"conversation    : {conversation.title if conversation else '(new)'}")
        print(f"user message    : {args.message!r} ({len(args.message)} chars)")
        print()

        history_chars = sum(len(m.content) for m in context.short_term)
        rows = [
            ("system prompt (scope + task + contract)", len(system_prompt)),
            ("personalization context", len(context.context_block)),
            (f"short-term history ({len(context.short_term)} msgs)", history_chars),
            ("the request itself", len(context.user_request)),
        ]
        total = sum(n for _, n in rows) or 1
        print(f"{'component':<42}{'chars':>8}{'~tokens':>9}{'share':>8}")
        print("-" * 67)
        for label, chars in rows:
            print(f"{label:<42}{chars:>8}{chars // 4:>9}{(chars / total * 100):>7.0f}%")
        print("-" * 67)
        print(f"{'TOTAL PROMPT':<42}{total:>8}{total // 4:>9}")
        print()

        print("within the personalization context:")
        for label, lines in (
            ("global profile", context.global_summary),
            (f"{spec.domain} domain profile", context.domain_summary),
            ("agent profile", context.agent_summary),
        ):
            rendered = "; ".join(lines) if lines else "(not set up)"
            print(f"  {label:<26}{len(lines):>3} lines  {rendered[:70]}")
        print(f"  {'memories retrieved':<26}{len(context.memories):>3}")
        for scored in context.memories[:5]:
            scope = scored.memory.agent_key or scored.memory.domain or "global"
            print(f"      [{scope}] {scored.memory.content[:58]}")
        print()

        prompt_tokens = total / 4
        out_tokens = agent.max_tokens(context)
        print(f"max output tokens configured  : {out_tokens}")
        print(
            f"estimated prompt eval         : {prompt_tokens / PROMPT_TOKENS_PER_SEC:6.0f}s "
            f"({PROMPT_TOKENS_PER_SEC:.0f} tok/s in)"
        )
        print(
            f"estimated generation (worst)  : {out_tokens / OUTPUT_TOKENS_PER_SEC:6.0f}s "
            f"({OUTPUT_TOKENS_PER_SEC:.1f} tok/s out)"
        )
        print(
            f"estimated total (worst)       : "
            f"{prompt_tokens / PROMPT_TOKENS_PER_SEC + out_tokens / OUTPUT_TOKENS_PER_SEC:6.0f}s"
        )
        print()
        print(
            f"limits: SHORT_TERM_WINDOW={settings.SHORT_TERM_WINDOW} msgs, "
            f"SHORT_TERM_MAX_CHARS={settings.SHORT_TERM_MAX_CHARS}, "
            f"LLM_MAX_TOKENS={settings.LLM_MAX_TOKENS}, "
            f"TRIVIAL_REPLY_MAX_TOKENS={settings.TRIVIAL_REPLY_MAX_TOKENS}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
