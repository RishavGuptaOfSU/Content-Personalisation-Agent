#!/usr/bin/env python
"""Live check against a *running* server and the real model.

Unlike ``verify_pipeline.py`` (which drives the app in-process with TestClient),
this talks HTTP to an already running backend, so it verifies the deployed
process, the real provider and the media endpoint end to end.

    python scripts/live_check.py                       # all steps
    python scripts/live_check.py --base http://127.0.0.1:8000
    python scripts/live_check.py --only image,copy

On CPU-only hardware the text steps take a minute or two each; the image steps
are faster because their JSON spec is short.
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

BRAND = {
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
    "marketing.ad-creative": {"objective": "Free trial signups", "size": "Square 1080x1080"},
    "marketing.social-copy": {
        "platforms": ["LinkedIn"],
        "length": "Short (50-120)",
        "use_hashtags": "Yes, a few",
    },
    "marketing.seo-optimizer": {"content_type": "Landing page", "region": "India, English"},
    "marketing.campaign-planner": {
        "goal": "Lead generation",
        "channels": ["LinkedIn", "Email"],
        "budget": "Small (<$500/mo)",
    },
}


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
        help="Comma-separated steps: catalog,setup,image,ad,copy,seo,campaign,scope,memory,dashboard",
    )
    parser.add_argument("--timeout", type=float, default=900.0)
    args = parser.parse_args()
    steps = {s.strip() for s in args.only.split(",") if s.strip()}

    def want(step: str) -> bool:
        return not steps or step in steps

    client = httpx.Client(base_url=args.base, timeout=args.timeout)
    headers: dict[str, str] = {}

    def chat(message: str, agent_key: str, **extra) -> dict:
        started = time.perf_counter()
        response = client.post(
            "/api/chat",
            headers=headers,
            json={"message": message, "agent_key": agent_key, **extra},
        )
        elapsed = time.perf_counter() - started
        if response.status_code != 200:
            check(
                f"chat with {agent_key}",
                False,
                f"HTTP {response.status_code} {response.text[:200]}",
            )
            return {}
        body = response.json()
        print(
            f"    [{agent_key.split('.')[-1]}] {elapsed:.1f}s · "
            f"{body['assistant_message']['output_kind']} · "
            f"{len(body['assistant_message']['content'])} chars",
            flush=True,
        )
        return body

    def verify_png(media: dict, expected: tuple[int, int] | None = None) -> None:
        if expected:
            check(
                "rendered at the configured size",
                (media["width"], media["height"]) == expected,
                f"{media['width']}x{media['height']}",
            )
        check("alt text present", bool(media["alt_text"]), media["alt_text"][:60])
        served = client.get(media["url"])
        check(
            "the media URL serves a real PNG",
            served.status_code == 200
            and served.content[:8] == b"\x89PNG\r\n\x1a\n"
            and len(served.content) > 5000,
            f"{served.status_code}, {len(served.content)} bytes",
        )
        print(f"    saved: {media['filename']}")

    section("0. Server and catalog")
    health = client.get("/health").json()
    check("health ok", health["status"] == "ok", health["database"]["dialect"])
    provider = health["providers"]["llm"]
    check(
        "a real model is configured",
        provider["provider"] != "local-dev",
        f"{provider['provider']}/{provider['model']}",
    )
    check("the model is pulled", provider.get("model_pulled") is not False)

    overview = client.get("/api/catalog").json()
    check(
        "one domain / five agents",
        overview["domains"] == 1 and overview["agents"] == 5,
        str(overview["by_domain"]),
    )
    check(
        "two image agents, three text agents",
        overview["output_kinds"]["image"] == 2 and overview["output_kinds"]["text"] == 3,
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
    headers["Authorization"] = f"Bearer {registered.json()['access_token']}"

    section("2. Two-step setup: brand profile, then each agent")
    brand = client.put(
        "/api/profile/domain/marketing", headers=headers, json={"profile_data": BRAND}
    )
    check("brand profile saved", brand.status_code == 200 and brand.json()["is_configured"])
    sibling = client.get("/api/profile/agent/marketing.social-copy", headers=headers).json()
    check(
        "agents reuse the brand answers but need their own",
        sibling["domain_configured"] is True and sibling["agent_configured"] is False,
    )
    for key, data in AGENT_PROFILES.items():
        client.put(f"/api/profile/agent/{key}", headers=headers, json={"profile_data": data})
    configured = [
        a for a in client.get("/api/agents", headers=headers).json() if a["is_configured"]
    ]
    check("all five agents configured", len(configured) == 5, f"{len(configured)}/5")

    if want("image"):
        section("3. Post image — real model designs it, renderer produces the PNG")
        body = chat(
            "Create a LinkedIn post image about cutting cloud costs with automation",
            "marketing.post-image",
        )
        if body:
            message = body["assistant_message"]
            check("output_kind is image", message["output_kind"] == "image")
            check("one media item attached", len(message["media"]) == 1)
            if message["media"]:
                verify_png(message["media"][0], (1200, 627))
                spec = message["media"][0].get("spec") or {}
                check(
                    "the headline came from the model, not the raw request",
                    bool(spec.get("headline")),
                    str(spec.get("headline"))[:70],
                )

    if want("ad"):
        section("4. Ad creative — its own size and an offer-led layout")
        body = chat("Ad creative promoting our free trial", "marketing.ad-creative")
        if body:
            message = body["assistant_message"]
            check("output_kind is image", message["output_kind"] == "image")
            if message["media"]:
                verify_png(message["media"][0], (1080, 1080))

    if want("copy"):
        section("5. Social caption writer")
        body = chat(
            "Write a LinkedIn post about how much cloud spend sits idle",
            "marketing.social-copy",
        )
        if body:
            message = body["assistant_message"]
            check("output_kind is text", message["output_kind"] == "text")
            check("no media on a text agent", message["media"] == [])
            check(
                "the brand name reached the prompt",
                any("Acme Cloud" in line for line in body["personalization"]["domain_profile_summary"]),
                "; ".join(body["personalization"]["domain_profile_summary"])[:70],
            )
            check(
                "produced usable copy",
                len(message["content"]) > 120,
                f"{len(message['content'])} chars",
            )

    if want("seo"):
        section("6. SEO optimizer")
        body = chat(
            "Title tag and meta description for our cloud cost automation landing page",
            "marketing.seo-optimizer",
        )
        if body:
            content = body["assistant_message"]["content"].lower()
            check("output_kind is text", body["assistant_message"]["output_kind"] == "text")
            check(
                "produced the declared SEO sections",
                "title" in content and ("meta" in content or "keyword" in content),
                body["assistant_message"]["content"][:80].replace("\n", " "),
            )

    if want("campaign"):
        section("7. Campaign planner")
        body = chat(
            "Plan a two week launch campaign for our cost automation feature",
            "marketing.campaign-planner",
        )
        if body:
            content = body["assistant_message"]["content"].lower()
            check(
                "produced the declared plan sections",
                "objective" in content and ("channel" in content or "kpi" in content),
                body["assistant_message"]["content"][:80].replace("\n", " "),
            )

    if want("scope"):
        section("8. Scope guard — siblings hand off, with no model call")
        body = chat("Create the post image graphic for our launch", "marketing.social-copy")
        if body:
            check(
                "scope.in_scope is false",
                body["scope"]["in_scope"] is False,
                body["scope"]["reason"],
            )
            check(
                "handed off to the post image agent",
                body["scope"]["suggested_agent_key"] == "marketing.post-image",
                str(body["scope"]["suggested_agent_key"]),
            )
            check(
                "no model call was spent",
                body["assistant_message"]["meta"]["provider"] == "scope-guard",
                str(body["assistant_message"]["meta"]["provider"]),
            )

    if want("memory"):
        section("9. Memory scope isolation between siblings")
        taught = client.post(
            "/api/memory",
            headers=headers,
            json={
                "content": "Always end captions with a question",
                "agent_key": "marketing.social-copy",
                "kind": "preference",
                "importance": 0.8,
            },
        )
        check("POST /memory -> 201", taught.status_code == 201, str(taught.status_code))
        if taught.status_code == 201:
            check(
                "agent memory also records its domain",
                taught.json()["domain"] == "marketing",
                f"{taught.json()['agent_key']} / {taught.json()['domain']}",
            )
        found = client.get(
            "/api/memory/search",
            headers=headers,
            params={"q": "how should captions end?", "agent_key": "marketing.social-copy"},
        ).json()
        check(
            "semantic search finds it for its own agent",
            any("end captions" in m["content"].lower() for m in found),
            "; ".join(m["content"] for m in found)[:70],
        )
        other = client.get(
            "/api/memory/search",
            headers=headers,
            params={"q": "how should captions end?", "agent_key": "marketing.seo-optimizer"},
        ).json()
        check(
            "the same search returns nothing for a sibling",
            not any("end captions" in m["content"].lower() for m in other),
            f"{len(other)} results",
        )

    if want("dashboard"):
        section("10. Dashboard")
        stats = client.get("/api/dashboard/stats", headers=headers).json()
        check(
            "one domain / five agents counted",
            stats["total_domains"] == 1 and stats["total_agents"] == 5,
        )
        check(
            "generated images are counted",
            stats["images_generated"] >= 1,
            str(stats["images_generated"]),
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
