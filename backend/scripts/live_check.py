#!/usr/bin/env python
"""Live check against a *running* server and the real model.

Unlike ``verify_pipeline.py`` (which drives the app in-process with TestClient),
this talks HTTP to an already running backend, so it verifies the deployed
process, the real provider and the media endpoint end to end.

    python scripts/live_check.py                       # all steps
    python scripts/live_check.py --base http://127.0.0.1:8000
    python scripts/live_check.py --only image,chart

Each step prints what it asserted. On CPU-only hardware the text steps take a
minute or two each; the visual steps are faster because their JSON spec is short.
"""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "\033[92m✓\033[0m" if condition else "\033[91m✗\033[0m"
    print(f"  {mark} {label}" + (f" — {detail}" if detail else ""), flush=True)
    (PASSED if condition else FAILED).append(label)


def section(title: str) -> None:
    print(f"\n\033[1m{title}\033[0m", flush=True)


def main() -> int:  # noqa: PLR0915 - a linear script
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--only",
        default="",
        help="Comma-separated steps: catalog,setup,text,scope,image,chart,memory,dashboard",
    )
    parser.add_argument("--timeout", type=float, default=900.0)
    args = parser.parse_args()
    steps = {s.strip() for s in args.only.split(",") if s.strip()}

    def want(step: str) -> bool:
        return not steps or step in steps

    client = httpx.Client(base_url=args.base, timeout=args.timeout)

    def chat(message: str, agent_key: str, **extra) -> dict:
        started = time.perf_counter()
        response = client.post(
            "/api/chat",
            headers=headers,
            json={"message": message, "agent_key": agent_key, **extra},
        )
        elapsed = time.perf_counter() - started
        if response.status_code != 200:
            # A 502 here means the provider is down, not that the app is wrong —
            # record it as a failure so the run cannot pass silently.
            check(f"chat with {agent_key}", False, f"HTTP {response.status_code} {response.text[:200]}")
            return {}
        body = response.json()
        print(
            f"    [{agent_key}] {elapsed:.1f}s · {body['assistant_message']['output_kind']}"
            f" · {len(body['assistant_message']['content'])} chars",
            flush=True,
        )
        return body

    section("0. Server and catalog")
    health = client.get("/health").json()
    check("health ok", health["status"] == "ok", health["database"]["dialect"])
    provider = health["providers"]["llm"]
    check("a real model is configured", provider["provider"] != "local-dev", f"{provider['provider']}/{provider['model']}")
    check("the model is pulled", provider.get("model_pulled") is not False)

    overview = client.get("/api/catalog").json()
    check("7 domains / 34 agents", overview["domains"] == 7 and overview["agents"] == 34, str(overview["by_domain"]))
    check(
        "3 image agents + 1 chart agent",
        overview["output_kinds"] == {"text": 30, "image": 3, "chart": 1},
        str(overview["output_kinds"]),
    )

    section("1. Register a throwaway account")
    email = f"live+{uuid.uuid4().hex[:8]}@example.com"
    registered = client.post(
        "/api/auth/register",
        json={"name": "Live Check", "email": email, "password": "LivePass123"},
    )
    check("register -> 201", registered.status_code == 201, str(registered.status_code))
    if registered.status_code != 201:
        print(registered.text)
        return 1
    headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}

    if want("catalog"):
        section("2. Two-level browse")
        domains = client.get("/api/domains", headers=headers).json()
        check("GET /domains lists 7 cards", len(domains) == 7)
        marketing_agents = client.get("/api/domains/marketing/agents", headers=headers).json()
        check(
            "marketing holds 5 narrow agents",
            len(marketing_agents) == 5,
            ", ".join(a["slug"] for a in marketing_agents),
        )
        post_image = next(a for a in marketing_agents if a["slug"] == "post-image")
        check("post-image declares output_kind=image", post_image["output_kind"] == "image")

    section("3. Two-step setup (domain, then agent)")
    client.put(
        "/api/profile/domain/marketing",
        headers=headers,
        json={
            "profile_data": {
                "brand_name": "Acme Cloud",
                "industry": "SaaS / Software",
                "audience": ["Developers", "Founders"],
                "tone": "Professional",
                "brand_colors": "#4F46E5, #0F172A",
                "avoid": ["clickbait", "emojis"],
            }
        },
    )
    client.put(
        "/api/profile/agent/marketing.post-image",
        headers=headers,
        json={
            "profile_data": {
                "platform": "LinkedIn",
                "style": "Bold type",
                "include_logo_text": "ACME CLOUD",
            }
        },
    )
    status = client.get("/api/profile/agent/marketing.post-image", headers=headers).json()
    check(
        "post-image is fully configured",
        status["needs_setup"] is False,
        f"domain={status['domain_configured']} agent={status['agent_configured']}",
    )
    sibling = client.get("/api/profile/agent/marketing.social-copy", headers=headers).json()
    check(
        "sibling reuses the domain answers, needs only its own",
        sibling["domain_configured"] is True and sibling["agent_configured"] is False,
    )

    if want("image"):
        section("4. Image agent — real model designs it, renderer produces the PNG")
        body = chat(
            "Create a LinkedIn post image about cutting cloud costs with automation",
            "marketing.post-image",
        )
        if body:
            message = body["assistant_message"]
            check("output_kind is image", message["output_kind"] == "image", message["output_kind"])
            check("one media item attached", len(message["media"]) == 1)
            if message["media"]:
                media = message["media"][0]
                check(
                    "LinkedIn dimensions from the agent profile",
                    (media["width"], media["height"]) == (1200, 627),
                    f"{media['width']}x{media['height']}",
                )
                check("alt text present", bool(media["alt_text"]), media["alt_text"][:70])
                served = client.get(media["url"])
                check(
                    "the media URL serves a real PNG",
                    served.status_code == 200
                    and served.content[:8] == b"\x89PNG\r\n\x1a\n"
                    and len(served.content) > 5000,
                    f"{served.status_code}, {len(served.content)} bytes",
                )
                spec = media.get("spec") or {}
                check(
                    "the headline came from the model, not the raw request",
                    bool(spec.get("headline")),
                    str(spec.get("headline"))[:70],
                )
                print(f"    saved: {media['filename']}")

    if want("chart"):
        section("5. Chart agent — plots only the numbers it was given")
        client.put(
            "/api/profile/domain/analytics",
            headers=headers,
            json={
                "profile_data": {
                    "experience": "Intermediate",
                    "tools": ["Python / pandas", "SQL"],
                    "domain_context": "B2B SaaS revenue",
                }
            },
        )
        client.put(
            "/api/profile/agent/analytics.chart-builder",
            headers=headers,
            json={"profile_data": {"style": "Clean light", "default_chart": "Bar", "show_values": "Yes"}},
        )
        body = chat(
            "Chart this monthly revenue: Jan 120, Feb 150, Mar 180, Apr 165, May 210",
            "analytics.chart-builder",
        )
        if body:
            message = body["assistant_message"]
            check("output_kind is chart", message["output_kind"] == "chart", message["output_kind"])
            check("a chart file was attached", len(message["media"]) == 1)
            if message["media"]:
                media = message["media"][0]
                spec = media.get("spec") or {}
                labels = [str(label) for label in (spec.get("labels") or [])]
                check(
                    "labels are the ones supplied",
                    {"Jan", "Feb", "Mar"}.issubset(set(labels)),
                    ", ".join(labels),
                )
                values = (spec.get("series") or [{}])[0].get("values") or []
                check(
                    "values are not invented",
                    [float(v) for v in values][:3] == [120.0, 150.0, 180.0],
                    str(values),
                )
                served = client.get(media["url"])
                check(
                    "the chart URL serves a real PNG",
                    served.status_code == 200 and served.content[:8] == b"\x89PNG\r\n\x1a\n",
                    f"{served.status_code}, {len(served.content)} bytes",
                )
                print(f"    saved: {media['filename']}")

    if want("text"):
        section("6. Text agent — a narrow tutor")
        client.put(
            "/api/profile/domain/education",
            headers=headers,
            json={
                "profile_data": {
                    "board": "CBSE",
                    "language": "English",
                    "learning_style": ["Step-by-step working"],
                    "exam_target": "Class 10 boards",
                }
            },
        )
        client.put(
            "/api/profile/agent/education.class10-maths",
            headers=headers,
            json={
                "profile_data": {
                    "weak_chapters": ["Trigonometry"],
                    "detail_level": "Every single step",
                }
            },
        )
        body = chat(
            "Solve: find the roots of x squared minus 5x plus 6 equals 0",
            "education.class10-maths",
        )
        if body:
            content = body["assistant_message"]["content"]
            check("output_kind is text", body["assistant_message"]["output_kind"] == "text")
            check("no media on a text agent", body["assistant_message"]["media"] == [])
            check(
                "the board reached the prompt",
                any("CBSE" in line for line in body["personalization"]["domain_profile_summary"]),
                "; ".join(body["personalization"]["domain_profile_summary"])[:70],
            )
            check(
                "the answer mentions the roots 2 and 3",
                "2" in content and "3" in content,
                content[:90].replace("\n", " "),
            )

    if want("scope"):
        section("7. Scope guard — the tutor refuses Python and hands off")
        body = chat(
            "Explain Python decorators and how functools.wraps preserves metadata",
            "education.class10-maths",
        )
        if body:
            check("scope.in_scope is false", body["scope"]["in_scope"] is False, body["scope"]["reason"])
            check(
                "handed off to a technical agent",
                (body["scope"]["suggested_agent_key"] or "").startswith("technical."),
                str(body["scope"]["suggested_agent_key"]),
            )
            check(
                "no model call was spent",
                body["assistant_message"]["meta"]["provider"] == "scope-guard",
                str(body["assistant_message"]["meta"]["provider"]),
            )

    if want("memory"):
        section("8. Memory scope isolation")
        response = client.post(
            "/api/memory",
            headers=headers,
            json={
                "content": "Always label the diagram axes in maths answers",
                "agent_key": "education.class10-maths",
                "kind": "preference",
                "importance": 0.8,
            },
        )
        check(
            "POST /memory -> 201",
            response.status_code == 201,
            f"{response.status_code} {response.text[:120]}",
        )
        taught = response.json() if response.status_code == 201 else {}
        check(
            "agent memory also records its domain",
            taught.get("agent_key") == "education.class10-maths"
            and taught.get("domain") == "education",
            f"{taught.get('agent_key')} / {taught.get('domain')}",
        )
        found = client.get(
            "/api/memory/search",
            headers=headers,
            params={"q": "how should maths diagrams be drawn?", "agent_key": "education.class10-maths"},
        ).json()
        check(
            "semantic search finds it for its own agent",
            any("diagram axes" in m["content"].lower() for m in found),
            "; ".join(m["content"] for m in found)[:80],
        )
        other = client.get(
            "/api/memory/search",
            headers=headers,
            params={"q": "how should maths diagrams be drawn?", "agent_key": "marketing.post-image"},
        ).json()
        check(
            "the same search returns nothing for another agent",
            not any("diagram axes" in m["content"].lower() for m in other),
            f"{len(other)} results",
        )

    if want("dashboard"):
        section("9. Dashboard reflects the two levels")
        stats = client.get("/api/dashboard/stats", headers=headers).json()
        check("7 domains / 34 agents counted", stats["total_domains"] == 7 and stats["total_agents"] == 34)
        check(
            "generated images and charts are counted",
            stats["images_generated"] >= 1,
            str(stats["images_generated"]),
        )
        domains = client.get("/api/domains", headers=headers).json()
        marketing = next(d for d in domains if d["key"] == "marketing")
        check(
            "the marketing card shows its configured agent",
            marketing["configured_agents"] >= 1,
            f"{marketing['configured_agents']}/{marketing['agent_count']}",
        )

    client.close()

    print("\n" + "=" * 68)
    print(f"\033[1mPASSED: {len(PASSED)}   FAILED: {len(FAILED)}\033[0m")
    if FAILED:
        print("\nFailures:")
        for label in FAILED:
            print(f"  - {label}")
    print("=" * 68)
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
