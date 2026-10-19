#!/usr/bin/env python
"""Controlled A/B checks that personalization actually reaches the output.

The evaluation suite measures whether an agent does its job. This measures
something different and easy to fake: whether changing the *profile* or the
*memory* changes what comes back, and whether scopes stay isolated.

Each scenario sends the **same request** under two different configurations and
compares. Assertions come in two kinds:

* **structural** — what the pipeline assembled (profile summaries, which
  memories were retrieved and at which scope). These work with any provider,
  including ``LLM_PROVIDER=mock``, and are the ones that prove isolation.
* **generative** — whether the produced text actually differs and carries the
  right brand. These need a real model to mean anything and are skipped under
  the mock provider.

    python scripts/personalization_check.py
    DATABASE_URL=sqlite:////tmp/pc.db LLM_PROVIDER=mock \
        python scripts/personalization_check.py      # structural only
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("APP_ENV", "development")

from fastapi.testclient import TestClient  # noqa: E402

from app.agents.definitions import PRIMARY_DOMAIN  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []
SKIPPED: list[str] = []

BRAND_A = {
    "brand_name": "Acme Cloud",
    "industry": "SaaS / Software",
    "audience": ["Developers", "Founders"],
    "tone": "Professional",
    "brand_colors": "#4F46E5, #0F172A",
    "avoid": ["clickbait", "emojis"],
}
BRAND_B = {
    "brand_name": "Bloom Bakery",
    "industry": "Food & Beverage",
    "audience": ["Consumers", "Small businesses"],
    "tone": "Friendly",
    "brand_colors": "#E11D48, #FFF1F2",
    "avoid": ["corporate jargon"],
}
COPY_PROFILE = {
    "platforms": ["LinkedIn"],
    "length": "Short (50-120)",
    "use_hashtags": "Yes, a few",
}
SEO_PROFILE = {"content_type": "Landing page", "region": "India, English"}

REAL_MODEL = settings.LLM_PROVIDER != "mock"


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(label)
        print(f"  \033[92m✓\033[0m {label}" + (f" — {detail}" if detail else ""))
    else:
        FAILED.append(label)
        print(f"  \033[91m✗\033[0m {label}" + (f" — {detail}" if detail else ""))


def skip(label: str, why: str) -> None:
    SKIPPED.append(label)
    print(f"  \033[90m–\033[0m {label} (skipped: {why})")


def section(title: str) -> None:
    print(f"\n\033[1m{title}\033[0m")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


class Harness:
    """One registered user, with helpers to reconfigure and send requests."""

    def __init__(self, client: TestClient, label: str) -> None:
        self.client = client
        email = f"pc-{label}-{uuid.uuid4().hex[:6]}@example.com"
        self.headers = {
            "Authorization": "Bearer "
            + client.post(
                "/api/auth/register",
                json={"name": f"PC {label}", "email": email, "password": "PcPass123"},
            ).json()["access_token"]
        }

    def set_brand(self, data: dict[str, Any]) -> None:
        self.client.put(
            f"/api/profile/domain/{PRIMARY_DOMAIN}",
            headers=self.headers,
            json={"profile_data": data},
        )

    def set_agent(self, agent_key: str, data: dict[str, Any]) -> None:
        self.client.put(
            f"/api/profile/agent/{agent_key}", headers=self.headers, json={"profile_data": data}
        )

    def remember(self, content: str, **scope: Any) -> dict[str, Any]:
        return self.client.post(
            "/api/memory",
            headers=self.headers,
            json={"content": content, "kind": "preference", "importance": 0.8, **scope},
        ).json()

    def ask(self, message: str, agent_key: str) -> dict[str, Any]:
        response = self.client.post(
            "/api/chat",
            headers=self.headers,
            json={"message": message, "agent_key": agent_key},
        )
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
        return response.json()


def main() -> int:  # noqa: PLR0915 - a linear set of scenarios
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only", default="", help="Comma-separated: brand,tone,scope,override"
    )
    args = parser.parse_args()
    steps = {s.strip() for s in args.only.split(",") if s.strip()}

    def want(step: str) -> bool:
        return not steps or step in steps

    print(f"provider: {settings.LLM_PROVIDER}")
    print(f"generative assertions: {'enabled' if REAL_MODEL else 'SKIPPED (mock provider)'}")

    request = "Write a LinkedIn post about why our customers come back"

    with TestClient(app) as client:
        if want("brand"):
            section("1. Same request, two different brands")
            a = Harness(client, "brand-a")
            a.set_brand(BRAND_A)
            a.set_agent("marketing.social-copy", COPY_PROFILE)
            b = Harness(client, "brand-b")
            b.set_brand(BRAND_B)
            b.set_agent("marketing.social-copy", COPY_PROFILE)

            out_a = a.ask(request, "marketing.social-copy")
            out_b = b.ask(request, "marketing.social-copy")

            summary_a = " ".join(out_a["personalization"]["domain_profile_summary"])
            summary_b = " ".join(out_b["personalization"]["domain_profile_summary"])
            check("brand A's profile reached its prompt", "Acme Cloud" in summary_a, summary_a[:60])
            check("brand B's profile reached its prompt", "Bloom Bakery" in summary_b, summary_b[:60])
            check("the two prompts carried different brands", summary_a != summary_b)
            check(
                "brand A's prompt does not mention brand B",
                "Bloom" not in summary_a and "Bakery" not in summary_a,
            )

            text_a = out_a["assistant_message"]["content"]
            text_b = out_b["assistant_message"]["content"]
            if REAL_MODEL:
                check(
                    "the two replies are not identical",
                    normalize(text_a) != normalize(text_b),
                    f"{len(text_a)} vs {len(text_b)} chars",
                )
                check(
                    "brand B's reply does not mention brand A",
                    "acme" not in text_b.lower(),
                    text_b[:70].replace("\n", " "),
                )
            else:
                skip("the two replies are not identical", "needs a real model")
                skip("brand B's reply does not mention brand A", "needs a real model")

        if want("tone"):
            section("2. Same request and brand, two different tones")
            bold = Harness(client, "tone-bold")
            bold.set_brand({**BRAND_A, "tone": "Bold"})
            bold.set_agent("marketing.social-copy", COPY_PROFILE)
            corporate = Harness(client, "tone-corp")
            corporate.set_brand({**BRAND_A, "tone": "Corporate"})
            corporate.set_agent("marketing.social-copy", COPY_PROFILE)

            out_bold = bold.ask(request, "marketing.social-copy")
            out_corp = corporate.ask(request, "marketing.social-copy")

            check(
                "the bold tone is in its prompt",
                "Bold" in " ".join(out_bold["personalization"]["domain_profile_summary"]),
            )
            check(
                "the corporate tone is in its prompt",
                "Corporate" in " ".join(out_corp["personalization"]["domain_profile_summary"]),
            )
            if REAL_MODEL:
                check(
                    "changing only the tone changed the reply",
                    normalize(out_bold["assistant_message"]["content"])
                    != normalize(out_corp["assistant_message"]["content"]),
                )
            else:
                skip("changing only the tone changed the reply", "needs a real model")

        if want("scope"):
            section("3. Memory scope isolation")
            user = Harness(client, "scopes")
            user.set_brand(BRAND_A)
            user.set_agent("marketing.social-copy", COPY_PROFILE)
            user.set_agent("marketing.seo-optimizer", SEO_PROFILE)

            agent_memory = user.remember(
                "Always end captions with a question", agent_key="marketing.social-copy"
            )
            brand_memory = user.remember(
                "Positions on engineering time saved, never on price", domain=PRIMARY_DOMAIN
            )
            global_memory = user.remember("Never use emoji")
            user.remember(
                "Prefers window seats on flights", agent_key="marketing.campaign-planner"
            )

            check(
                "agent memory stored with its agent and domain",
                agent_memory["agent_key"] == "marketing.social-copy"
                and agent_memory["domain"] == PRIMARY_DOMAIN,
                f"{agent_memory['agent_key']} / {agent_memory['domain']}",
            )
            check(
                "brand memory stored with no agent",
                brand_memory["agent_key"] is None and brand_memory["domain"] == PRIMARY_DOMAIN,
            )
            check(
                "global memory stored with neither scope",
                global_memory["agent_key"] is None and global_memory["domain"] is None,
            )

            copy_out = user.ask("Write a LinkedIn post about our pricing", "marketing.social-copy")
            seo_out = user.ask(
                "Optimise the pricing page title and meta", "marketing.seo-optimizer"
            )

            def used(body: dict[str, Any]) -> list[str]:
                return [m["content"].lower() for m in body["personalization"]["memories_used"]]

            def scopes(body: dict[str, Any]) -> set[str]:
                return {m["scope"] for m in body["personalization"]["memories_used"]}

            check(
                "its own agent memory reached the caption writer",
                any("end captions" in m for m in used(copy_out)),
                "; ".join(used(copy_out))[:80] or "(none)",
            )
            check(
                "the caption-only memory did NOT reach the SEO agent",
                not any("end captions" in m for m in used(seo_out)),
                "; ".join(used(seo_out))[:80] or "(none)",
            )
            check(
                "another agent's memory did NOT reach the caption writer",
                not any("window seats" in m for m in used(copy_out)),
            )
            check(
                "only global / brand / own-agent scopes were used by the caption writer",
                scopes(copy_out) <= {"global", PRIMARY_DOMAIN, "marketing.social-copy"},
                ", ".join(sorted(scopes(copy_out))) or "(none)",
            )
            check(
                "only global / brand / own-agent scopes were used by the SEO agent",
                scopes(seo_out) <= {"global", PRIMARY_DOMAIN, "marketing.seo-optimizer"},
                ", ".join(sorted(scopes(seo_out))) or "(none)",
            )

            summary = client.get("/api/memory/summary", headers=user.headers).json()
            check(
                "the summary separates brand-wide from global",
                set(summary["by_domain"]) == {PRIMARY_DOMAIN, "global"},
                str(summary["by_domain"]),
            )

        if want("override"):
            section("4. A newer preference supersedes an older one")
            user = Harness(client, "override")
            user.set_brand(BRAND_A)
            user.set_agent("marketing.social-copy", COPY_PROFILE)

            user.remember("Wants long, detailed LinkedIn posts", agent_key="marketing.social-copy")
            newer = user.remember(
                "Wants LinkedIn posts kept under 60 words", agent_key="marketing.social-copy"
            )
            check("the newer preference was stored", bool(newer.get("id")))

            out = user.ask("Write a LinkedIn post about our uptime", "marketing.social-copy")
            retrieved = [m["content"] for m in out["personalization"]["memories_used"]]
            check(
                "the newer preference was retrieved",
                any("under 60 words" in m for m in retrieved),
                "; ".join(retrieved)[:90] or "(none)",
            )
            # Both can legitimately be retrieved; what matters is the newer one is
            # present so the prompt carries the current instruction.
            if REAL_MODEL:
                words = len(out["assistant_message"]["content"].split())
                check(
                    "the reply respected the shorter preference (<=160 words)",
                    words <= 160,
                    f"{words} words",
                )
            else:
                skip("the reply respected the shorter preference", "needs a real model")

            repeat = user.remember(
                "Wants LinkedIn posts kept under 60 words", agent_key="marketing.social-copy"
            )
            check(
                "repeating a preference reinforces instead of duplicating",
                repeat["id"] == newer["id"] and repeat["occurrences"] >= 2,
                f"id match={repeat['id'] == newer['id']} occurrences={repeat.get('occurrences')}",
            )

    print("\n" + "=" * 68)
    print(
        f"\033[1mPASSED: {len(PASSED)}   FAILED: {len(FAILED)}   "
        f"SKIPPED: {len(SKIPPED)}\033[0m"
    )
    if FAILED:
        print("\nFailures:")
        for label in FAILED:
            print(f"  - {label}")
    if SKIPPED and not REAL_MODEL:
        print(
            f"\n{len(SKIPPED)} generative assertion(s) skipped under the mock provider. "
            "Re-run with LLM_PROVIDER=ollama to exercise them."
        )
    print("=" * 68)
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
