#!/usr/bin/env python
"""Exercise every agent in the catalog once and report what came back.

Each agent is set up (domain profile + agent profile, answered from the declared
field defaults) and then sent its own first example request. The check is that
the agent produced *its declared deliverable*: text agents must return prose,
image and chart agents must return a rendered file that exists on disk.

    python scripts/smoke_all_agents.py                       # all 34 agents
    python scripts/smoke_all_agents.py --domain marketing    # one domain
    python scripts/smoke_all_agents.py --agent marketing.post-image
    python scripts/smoke_all_agents.py --visual-only         # image/chart agents
    python scripts/smoke_all_agents.py --quiet               # table only

With ``LLM_PROVIDER=mock`` this runs in seconds. Against a real local model on
CPU expect roughly a minute per agent, so use ``--domain`` while iterating.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app.agents.catalog import AgentSpec, get_domain, list_agents  # noqa: E402
from app.main import app  # noqa: E402
from app.media import media_root  # noqa: E402

#: Requests that need concrete input the examples do not carry.
REQUEST_OVERRIDES: dict[str, str] = {
    "analytics.chart-builder": (
        "Chart this monthly revenue: Jan 120, Feb 150, Mar 180, Apr 165, May 210"
    ),
    "education.homework-solver": (
        "A train travels 240 km in 3 hours. Find its average speed in m/s."
    ),
    "career.resume-writer": (
        "Improve this bullet: 'Worked on backend APIs for the payments team.'"
    ),
}

#: Free-text fields that need a plausible answer to count as configured.
TEXT_ANSWERS: dict[str, str] = {
    "exam_date": "15 March 2027",
    "exam_target": "Class 10 board exam",
    "project_context": "A FastAPI + React personalization platform",
    "brand_name": "Acme Cloud",
    "brand_colors": "#4F46E5, #0F172A",
    "include_logo_text": "ACME CLOUD",
    "domain_context": "B2B SaaS revenue and product usage",
    "region": "India, English",
    "current_role": "Backend developer",
    "resume_text": "Backend developer, 3 years, Python and PostgreSQL.",
    "event_table": "events",
    "background": "Computer science undergraduate",
    "goal": "Understand the drivers of monthly revenue",
    "goals": "Lead generation",
    "target": "Product company interviews",
    "stack": "Python 3.12, FastAPI, PostgreSQL",
    "environment": "Local development and Docker",
}


def answer_field(field: Any) -> Any:
    """A plausible answer for one profile field, taken from its own declaration."""
    if field.default not in (None, "", []):
        return field.default
    if field.kind in ("multiselect", "tags"):
        return list(field.options[:2]) or ["General"]
    if field.kind == "select":
        return field.options[0] if field.options else "Default"
    if field.kind == "number":
        return 1
    return TEXT_ANSWERS.get(field.key, "Not specified")


def profile_for(fields: tuple) -> dict[str, Any]:
    return {field.key: answer_field(field) for field in fields}


def main() -> int:  # noqa: PLR0915 - a linear report
    parser = argparse.ArgumentParser(description="Smoke-test every agent")
    parser.add_argument("--domain", help="Only agents in this domain")
    parser.add_argument("--agent", help="Only this agent key")
    parser.add_argument("--visual-only", action="store_true", help="Only image/chart agents")
    parser.add_argument("--quiet", action="store_true", help="Suppress response bodies")
    parser.add_argument(
        "--min-chars",
        type=int,
        default=200,
        help="Flag text responses shorter than this (default 200)",
    )
    args = parser.parse_args()

    agents: list[AgentSpec] = list_agents(args.domain)
    if args.agent:
        agents = [spec for spec in agents if spec.key == args.agent.strip().lower()]
        if not agents:
            print(f"No such agent: {args.agent}")
            return 1
    if args.visual_only:
        agents = [spec for spec in agents if spec.output_kind.is_visual]

    rows: list[tuple[str, str, str, int, int, str]] = []
    failures: list[str] = []

    with TestClient(app) as client:
        email = f"smoke+{uuid.uuid4().hex[:8]}@example.com"
        token = client.post(
            "/api/auth/register",
            json={"name": "Smoke Test", "email": email, "password": "SmokePass123"},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        configured_domains: set[str] = set()

        for spec in agents:
            # --- setup: domain profile once, then this agent's own profile ----
            if spec.domain not in configured_domains:
                domain = get_domain(spec.domain)
                response = client.put(
                    f"/api/profile/domain/{spec.domain}",
                    headers=headers,
                    json={"profile_data": profile_for(domain.profile_fields)},
                )
                if response.status_code != 200:
                    failures.append(f"{spec.domain}: domain setup {response.status_code}")
                configured_domains.add(spec.domain)

            response = client.put(
                f"/api/profile/agent/{spec.key}",
                headers=headers,
                json={"profile_data": profile_for(spec.profile_fields)},
            )
            if response.status_code != 200:
                failures.append(f"{spec.key}: agent setup {response.status_code}")

            request_text = REQUEST_OVERRIDES.get(
                spec.key, spec.examples[0] if spec.examples else spec.scope
            )

            chat = client.post(
                "/api/chat",
                headers=headers,
                json={"message": request_text, "agent_key": spec.key},
            )

            if not args.quiet:
                print("\n" + "=" * 76)
                print(f"{spec.key}  ·  {spec.output_kind.value}")
                print(f"> {request_text}")
                print("=" * 76)

            if chat.status_code != 200:
                failures.append(f"{spec.key}: HTTP {chat.status_code}")
                print(f"FAILED ({chat.status_code}): {chat.text[:300]}")
                rows.append((spec.key, spec.output_kind.value, "HTTP error", 0, 0, ""))
                continue

            body = chat.json()
            message = body["assistant_message"]
            content = message["content"]
            media = message["media"]
            note = ""

            # --- the deliverable matches what the agent declares --------------
            if message["output_kind"] != spec.output_kind.value:
                failures.append(
                    f"{spec.key}: output_kind {message['output_kind']} "
                    f"!= declared {spec.output_kind.value}"
                )
                note = "wrong output kind"

            if spec.output_kind.is_visual:
                if not media:
                    failures.append(f"{spec.key}: no media returned")
                    note = note or "no media"
                else:
                    path = media_root() / media[0]["filename"]
                    if not path.is_file():
                        failures.append(f"{spec.key}: media file missing on disk")
                        note = note or "file missing"
                    elif not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                        failures.append(f"{spec.key}: media file is not a PNG")
                        note = note or "not a png"
                    else:
                        note = f"{media[0]['width']}x{media[0]['height']}"
                if media and not media[0].get("alt_text"):
                    note = (note + " · no alt text").strip(" ·")
            else:
                if media:
                    failures.append(f"{spec.key}: a text agent returned media")
                    note = note or "unexpected media"
                elif len(content) < args.min_chars:
                    failures.append(f"{spec.key}: only {len(content)} chars")
                    note = note or f"short ({len(content)})"

            if not args.quiet:
                print(content[:900])
                if len(content) > 900:
                    print(f"… [{len(content)} chars total]")
                if media:
                    item = media[0]
                    print(
                        f"\n[media] {item['url']} · {item['width']}x{item['height']} "
                        f"· {item['bytes']} bytes · {item['renderer']}"
                    )
                    print(f"[alt]   {item['alt_text']}")
                print(
                    f"\n-- {body['personalization']['context_characters']} context chars "
                    f"| {len(body['personalization']['memories_used'])} memories "
                    f"| {body['latency_ms']} ms"
                )

            rows.append(
                (
                    spec.key,
                    spec.output_kind.value,
                    note or "ok",
                    len(content),
                    body["latency_ms"],
                    media[0]["filename"] if media else "",
                )
            )

    print("\n" + "=" * 92)
    print(f"{'agent':<30}{'kind':<7}{'result':<20}{'chars':>7}{'ms':>7}  file")
    print("-" * 92)
    for key, kind, note, chars, latency, filename in rows:
        print(f"{key:<30}{kind:<7}{note:<20}{chars:>7}{latency:>7}  {filename}")
    print("=" * 92)

    if failures:
        print(f"\n{len(failures)} problem(s):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(f"\nAll {len(rows)} agents produced their declared deliverable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
