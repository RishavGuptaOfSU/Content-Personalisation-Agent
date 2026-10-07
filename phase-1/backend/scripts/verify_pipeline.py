#!/usr/bin/env python
"""End-to-end verification of the domain → agent platform.

Runs against the configured DATABASE_URL through FastAPI's TestClient, so it
exercises the real HTTP layer, real auth, real DB writes, the real LangGraph
pipeline, the real renderers and the real memory/feedback loop.

    python scripts/verify_pipeline.py

Use a throwaway database and the deterministic provider for a fast run::

    DATABASE_URL=sqlite:////tmp/verify.db LLM_PROVIDER=mock \
        python scripts/verify_pipeline.py

With ``LLM_PROVIDER=ollama`` the same script verifies the real model path; it
just takes minutes instead of seconds on CPU-only hardware.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app.agents.catalog import AGENTS, DOMAIN_ORDER, image_agents  # noqa: E402
from app.main import app  # noqa: E402
from app.media import media_root  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []

EXPECTED_DOMAINS = {
    "education",
    "technical",
    "career",
    "marketing",
    "analytics",
    "research",
    "creative",
}


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(label)
        print(f"  \033[92m✓\033[0m {label}" + (f" — {detail}" if detail else ""))
    else:
        FAILED.append(label)
        print(f"  \033[91m✗\033[0m {label}" + (f" — {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n\033[1m{title}\033[0m")


def main() -> int:
    with TestClient(app) as client:
        return run_journey(client)


# --------------------------------------------------------------------- helpers
def put_domain_profile(client: TestClient, headers: dict, domain: str, data: dict) -> Any:
    return client.put(
        f"/api/profile/domain/{domain}", headers=headers, json={"profile_data": data}
    )


def put_agent_profile(client: TestClient, headers: dict, agent_key: str, data: dict) -> Any:
    return client.put(
        f"/api/profile/agent/{agent_key}", headers=headers, json={"profile_data": data}
    )


def send(client: TestClient, headers: dict, message: str, **kwargs: Any) -> Any:
    payload: dict[str, Any] = {"message": message}
    payload.update(kwargs)
    return client.post("/api/chat", headers=headers, json=payload)


def sse_events(raw: str) -> list[tuple[str, Any]]:
    """Parse an SSE body into (event, data) pairs."""
    events: list[tuple[str, Any]] = []
    for block in raw.split("\n\n"):
        event = None
        data_lines: list[str] = []
        for line in block.splitlines():
            if line.startswith("event: "):
                event = line[len("event: ") :].strip()
            elif line.startswith("data: "):
                data_lines.append(line[len("data: ") :])
        if event is None:
            continue
        body = "\n".join(data_lines)
        try:
            events.append((event, json.loads(body) if body else None))
        except json.JSONDecodeError:
            events.append((event, body))
    return events


# --------------------------------------------------------------------- journey
def run_journey(client: TestClient) -> int:  # noqa: PLR0915 - a linear journey
    email = f"demo+{uuid.uuid4().hex[:8]}@example.com"
    password = "DemoPass123"

    section("0. Service health")
    health = client.get("/health").json()
    check("health endpoint reports ok", health["status"] == "ok", health["database"]["dialect"])
    check(
        "vector store selected",
        bool(health["database"]["vector_store"]),
        health["database"]["vector_store"],
    )
    provider_name = health["providers"]["llm"]["provider"]
    print(f"  · LLM provider: {provider_name} ({health['providers']['llm']['model']})")

    section("1. Catalog shape: domains contain many narrow agents")
    overview = client.get("/api/catalog").json()
    check("7 domains", overview["domains"] == 7, str(overview["domains"]))
    check(
        "agent count matches the catalog module",
        overview["agents"] == len(AGENTS),
        f"{overview['agents']} agents",
    )
    check(
        "every domain holds more than one agent",
        all(count > 1 for count in overview["by_domain"].values()),
        str(overview["by_domain"]),
    )
    check(
        "output kinds include image and chart",
        overview["output_kinds"].get("image", 0) >= 3
        and overview["output_kinds"].get("chart", 0) >= 1,
        str(overview["output_kinds"]),
    )
    check(
        "visual agents are the expected ones",
        set(overview["image_agents"])
        == {
            "marketing.post-image",
            "marketing.ad-creative",
            "analytics.chart-builder",
            "creative.poster-image",
        },
        ", ".join(sorted(overview["image_agents"])),
    )

    section("2. User registers and logs in")
    response = client.post(
        "/api/auth/register",
        json={"name": "Demo User", "email": email, "password": password},
    )
    check("POST /auth/register -> 201", response.status_code == 201, str(response.status_code))
    if response.status_code != 201:
        print(response.text)
        return 1
    check("register returns a JWT", bool(response.json().get("access_token")))
    check(
        "duplicate email rejected (409)",
        client.post(
            "/api/auth/register",
            json={"name": "Demo User", "email": email, "password": password},
        ).status_code
        == 409,
    )
    check(
        "weak password rejected (422)",
        client.post(
            "/api/auth/register",
            json={
                "name": "X",
                "email": f"weak+{uuid.uuid4().hex[:6]}@example.com",
                "password": "short",
            },
        ).status_code
        == 422,
    )

    login = client.post("/api/auth/login", json={"email": email, "password": password})
    check("POST /auth/login -> 200", login.status_code == 200)
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    check(
        "wrong password rejected (401)",
        client.post(
            "/api/auth/login", json={"email": email, "password": "WrongPass123"}
        ).status_code
        == 401,
    )
    check("protected route without token -> 401", client.get("/api/auth/me").status_code == 401)

    section("3. Dashboard level 1 — domain cards")
    domains = client.get("/api/domains", headers=headers)
    check("GET /domains -> 200", domains.status_code == 200)
    domain_list: list[dict[str, Any]] = domains.json()
    check("7 domain cards", len(domain_list) == 7, f"{len(domain_list)} domains")
    check(
        "all expected domains present",
        {d["key"] for d in domain_list} == EXPECTED_DOMAINS,
        ", ".join(d["key"] for d in domain_list),
    )
    check(
        "domain cards report their agent counts",
        all(d["agent_count"] > 1 for d in domain_list),
        ", ".join(f"{d['key']}={d['agent_count']}" for d in domain_list),
    )
    check(
        "every domain starts unconfigured",
        all(d["status_label"] == "Not configured" for d in domain_list),
    )
    marketing_card = next(d for d in domain_list if d["key"] == "marketing")
    check(
        "marketing card advertises its visual agents",
        "marketing.post-image" in marketing_card["visual_agents"],
        ", ".join(marketing_card["visual_agents"]),
    )
    check(
        "unknown domain -> 404",
        client.get("/api/domains/nope", headers=headers).status_code == 404,
    )

    section("4. Dashboard level 2 — agents inside a domain")
    edu_agents = client.get("/api/domains/education/agents", headers=headers)
    check("GET /domains/education/agents -> 200", edu_agents.status_code == 200)
    edu_list = edu_agents.json()
    check("education has 6 agents", len(edu_list) == 6, f"{len(edu_list)} agents")
    check(
        "agent keys are <domain>.<slug>",
        all(a["key"].startswith("education.") for a in edu_list),
        ", ".join(a["key"] for a in edu_list),
    )
    check(
        "class 10 maths and class 12 physics are separate agents",
        {"education.class10-maths", "education.class12-physics"}.issubset(
            {a["key"] for a in edu_list}
        ),
    )
    all_agents = client.get("/api/agents", headers=headers).json()
    check(
        f"GET /agents lists all {len(AGENTS)} agents",
        len(all_agents) == len(AGENTS),
        f"{len(all_agents)}",
    )
    check(
        "unknown agent -> 404",
        client.get("/api/agents/education.nope", headers=headers).status_code == 404,
    )

    section("5. Agent detail carries both setup forms")
    detail = client.get("/api/agents/education.class10-maths", headers=headers).json()
    check("output_kind is text", detail["output_kind"] == "text")
    check("scope sentence present", "Class 10" in detail["scope"], detail["scope"][:60])
    check(
        "out_of_scope lists what it refuses",
        any("physics" in item for item in detail["out_of_scope"]),
        "; ".join(detail["out_of_scope"])[:80],
    )
    check(
        "domain form asks the shared questions (board)",
        "board" in [f["key"] for f in detail["domain_profile_fields"]],
        ", ".join(f["key"] for f in detail["domain_profile_fields"]),
    )
    check(
        "agent form asks only its own questions",
        {"weak_chapters", "detail_level"} == {f["key"] for f in detail["profile_fields"]},
        ", ".join(f["key"] for f in detail["profile_fields"]),
    )
    check("needs_setup is true before setup", detail["needs_setup"] is True)

    section("6. Two-level setup: domain profile, then agent profile")
    domain_saved = put_domain_profile(
        client,
        headers,
        "education",
        {
            "board": "CBSE",
            "language": "English",
            "learning_style": ["Step-by-step working", "Practice questions"],
            "exam_target": "Class 10 board exam, March 2027",
        },
    )
    check("PUT /profile/domain/education -> 200", domain_saved.status_code == 200)
    check("domain profile marked configured", domain_saved.json()["is_configured"] is True)

    still_needs = client.get(
        "/api/profile/agent/education.class10-maths", headers=headers
    ).json()
    check(
        "agent still needs its own setup after the domain step",
        still_needs["domain_configured"] is True and still_needs["agent_configured"] is False,
        f"domain={still_needs['domain_configured']} agent={still_needs['agent_configured']}",
    )

    agent_saved = put_agent_profile(
        client,
        headers,
        "education.class10-maths",
        {
            "weak_chapters": ["Trigonometry", "Circles"],
            "detail_level": "Every single step",
        },
    )
    check("PUT /profile/agent/education.class10-maths -> 200", agent_saved.status_code == 200)
    check("agent profile marked configured", agent_saved.json()["is_configured"] is True)

    status = client.get("/api/profile/agent/education.class10-maths", headers=headers).json()
    check("needs_setup is now false", status["needs_setup"] is False)
    check("status label is Personalized", status["status_label"] == "Personalized")

    sibling = client.get("/api/profile/agent/education.class10-science", headers=headers).json()
    check(
        "a sibling agent reuses the domain profile but needs its own setup",
        sibling["domain_configured"] is True and sibling["agent_configured"] is False,
    )

    section("7. Chat with a narrow text agent")
    chat1 = send(
        client,
        headers,
        "Solve: find the roots of x squared minus 5x plus 6 equals 0",
        agent_key="education.class10-maths",
    )
    check("POST /chat -> 200", chat1.status_code == 200, str(chat1.status_code))
    if chat1.status_code != 200:
        print(chat1.text)
        return 1
    body1 = chat1.json()
    maths_conversation = body1["conversation_id"]
    check(
        "explicit selection overrode the router",
        body1["routing"]["agent_key"] == "education.class10-maths"
        and body1["routing"]["source"] == "explicit",
        body1["routing"]["source"],
    )
    check("routing reports the domain", body1["routing"]["domain"] == "education")
    check("request judged in scope", body1["scope"]["in_scope"] is True)
    check("assistant produced text", body1["assistant_message"]["output_kind"] == "text")
    check("assistant message has no media", body1["assistant_message"]["media"] == [])
    check(
        "domain profile reached the context (board)",
        any("CBSE" in line for line in body1["personalization"]["domain_profile_summary"]),
        "; ".join(body1["personalization"]["domain_profile_summary"])[:90],
    )
    check(
        "agent profile reached the context (weak chapters)",
        any(
            "Trigonometry" in line for line in body1["personalization"]["agent_profile_summary"]
        ),
        "; ".join(body1["personalization"]["agent_profile_summary"])[:90],
    )
    check(
        "the prompt carries the scope contract",
        "YOUR SCOPE" in body1["personalization"]["system_prompt_preview"]
        or "scope" in body1["personalization"]["system_prompt_preview"].lower(),
        body1["personalization"]["system_prompt_preview"][:70],
    )

    section("8. Scope guard hands off to the agent that owns the request")
    handoff = send(
        client,
        headers,
        "Explain Python decorators and how functools.wraps preserves metadata",
        agent_key="education.class10-maths",
    )
    check("out-of-scope request still -> 200", handoff.status_code == 200)
    hbody = handoff.json()
    check("scope.in_scope is false", hbody["scope"]["in_scope"] is False, hbody["scope"]["reason"])
    check(
        "handoff suggests a technical agent",
        (hbody["scope"]["suggested_agent_key"] or "").startswith("technical."),
        str(hbody["scope"]["suggested_agent_key"]),
    )
    check(
        "the reply names the agent that should handle it",
        hbody["scope"]["suggested_agent_name"] is not None
        and hbody["scope"]["suggested_agent_name"] in hbody["assistant_message"]["content"],
        hbody["assistant_message"]["content"][:90].replace("\n", " "),
    )
    check(
        "handoff is recorded on the message",
        hbody["assistant_message"]["meta"]["out_of_scope"] is True,
    )
    check(
        "no model call was spent on the handoff",
        hbody["assistant_message"]["meta"]["provider"] == "scope-guard",
        str(hbody["assistant_message"]["meta"]["provider"]),
    )
    check(
        "an in-scope short greeting is NOT handed off",
        send(
            client, headers, "hello", agent_key="education.class10-maths"
        ).json()["scope"]["in_scope"]
        is True,
    )

    section("9. Image agent returns a rendered graphic, not prose")
    put_domain_profile(
        client,
        headers,
        "marketing",
        {
            "brand_name": "Acme Cloud",
            "industry": "SaaS / Software",
            "audience": ["Developers", "Founders"],
            "tone": "Professional",
            "brand_colors": "#4F46E5, #0F172A",
            "avoid": ["clickbait", "emojis"],
        },
    )
    put_agent_profile(
        client,
        headers,
        "marketing.post-image",
        {
            "platform": "LinkedIn",
            "style": "Bold type",
            "include_logo_text": "ACME CLOUD",
        },
    )
    image_chat = send(
        client,
        headers,
        "Create a LinkedIn post image about cutting cloud costs with automation",
        agent_key="marketing.post-image",
    )
    check("image chat -> 200", image_chat.status_code == 200, str(image_chat.status_code))
    if image_chat.status_code != 200:
        print(image_chat.text)
        return 1
    ibody = image_chat.json()
    message = ibody["assistant_message"]
    check("output_kind is image", message["output_kind"] == "image", message["output_kind"])
    check("exactly one media item attached", len(message["media"]) == 1, str(len(message["media"])))
    if message["media"]:
        media = message["media"][0]
        check(
            "media url points at the media endpoint",
            media["url"].startswith("/api/media/"),
            media["url"],
        )
        check("mime type is an image", media["mime_type"].startswith("image/"), media["mime_type"])
        check(
            "rendered at the LinkedIn size from the agent profile",
            (media["width"], media["height"]) == (1200, 627),
            f"{media['width']}x{media['height']}",
        )
        check("alt text produced for accessibility", bool(media["alt_text"]), media["alt_text"][:70])
        on_disk = media_root() / media["filename"]
        check("file exists on disk", on_disk.is_file(), str(on_disk))
        if on_disk.is_file():
            head = on_disk.read_bytes()[:8]
            check("file really is a PNG", head.startswith(b"\x89PNG\r\n\x1a\n"), head.hex())
            check(
                "reported byte size matches the file",
                media["bytes"] == on_disk.stat().st_size,
                f"{media['bytes']} vs {on_disk.stat().st_size}",
            )
        served = client.get(media["url"])
        check("GET the media url -> 200", served.status_code == 200, str(served.status_code))
        check(
            "served with an image content type",
            served.headers.get("content-type", "").startswith("image/"),
            served.headers.get("content-type", ""),
        )
        check(
            "served bytes are the rendered PNG",
            served.content[:8] == b"\x89PNG\r\n\x1a\n" and len(served.content) > 1000,
            f"{len(served.content)} bytes",
        )
    check(
        "caption is short — the image is the deliverable",
        len(message["content"]) < 400,
        f"{len(message['content'])} chars",
    )
    check(
        "image agents are excluded from streaming",
        all(spec.output_kind.value != "text" for spec in image_agents()),
    )
    check("traversal on the media route refused", client.get("/api/media/..%2f..%2fapp%2fmain.py").status_code in (400, 404))

    section("10. Chart agent plots the data it was given")
    put_domain_profile(
        client,
        headers,
        "analytics",
        {
            "experience": "Intermediate",
            "tools": ["Python / pandas", "SQL"],
            "domain_context": "B2B SaaS revenue",
        },
    )
    put_agent_profile(
        client,
        headers,
        "analytics.chart-builder",
        {"style": "Clean light", "default_chart": "Bar", "show_values": "Yes"},
    )
    chart_chat = send(
        client,
        headers,
        "Chart this monthly revenue: Jan 120, Feb 150, Mar 180, Apr 165, May 210",
        agent_key="analytics.chart-builder",
    )
    check("chart chat -> 200", chart_chat.status_code == 200, str(chart_chat.status_code))
    cbody = chart_chat.json()
    cmessage = cbody["assistant_message"]
    check("output_kind is chart", cmessage["output_kind"] == "chart", cmessage["output_kind"])
    check("a chart image was attached", len(cmessage["media"]) == 1, str(len(cmessage["media"])))
    if cmessage["media"]:
        chart_media = cmessage["media"][0]
        chart_file = media_root() / chart_media["filename"]
        check("chart file exists on disk", chart_file.is_file(), str(chart_file))
        if chart_file.is_file():
            check(
                "chart file is a PNG of non-trivial size",
                chart_file.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
                and chart_file.stat().st_size > 5000,
                f"{chart_file.stat().st_size} bytes",
            )
        check("renderer recorded", bool(chart_media["renderer"]), chart_media["renderer"])
        labels = chart_media.get("spec", {}).get("labels") or []
        check(
            "labels came from the message, not invented",
            {"Jan", "Feb", "Mar"}.issubset({str(label) for label in labels}),
            ", ".join(str(label) for label in labels),
        )
    no_data = send(
        client,
        headers,
        "Please build me a chart of something interesting about the market",
        agent_key="analytics.chart-builder",
    ).json()
    check(
        "refuses to invent data when none is supplied",
        no_data["assistant_message"]["media"] == []
        and no_data["assistant_message"]["meta"]["incomplete_reason"] is not None,
        str(no_data["assistant_message"]["meta"]["incomplete_reason"]),
    )

    section("11. Router picks the right narrow agent (no explicit selection)")
    routing_cases = [
        ("Solve for x: 2x + 5 = 17 using the Class 10 method", "education.class10-maths"),
        ("Explain refraction of light through a glass slab", "education.class10-science"),
        ("Derive the electric field of a dipole on its axial line", "education.class12-physics"),
        ("Give me 10 MCQs on trigonometry with an answer key", "education.quiz-generator"),
        ("Make a 6 week revision timetable for my boards", "education.exam-planner"),
        ("Explain Python decorators with functools.wraps", "technical.python"),
        ("Why does my useEffect run twice in React?", "technical.react"),
        ("Optimise this SQL query with a LEFT JOIN returning duplicates", "technical.sql"),
        ("How do I solve two sum in O(n) time?", "technical.dsa"),
        ("Review this pull request for code quality", "technical.code-reviewer"),
        ("Create a LinkedIn post image about AI automation", "marketing.post-image"),
        ("Write a LinkedIn caption about AI automation", "marketing.social-copy"),
        ("Keyword research and meta description for our pricing page", "marketing.seo-optimizer"),
        ("Plan a two week launch campaign across channels", "marketing.campaign-planner"),
        ("Plot this data as a bar chart: Jan 10, Feb 20", "analytics.chart-builder"),
        ("What should I explore first in this sales dataset?", "analytics.eda-planner"),
        ("Improve my resume bullet points for a backend role", "career.resume-writer"),
        ("Help me prepare for a system design interview round", "career.interview-coach"),
        ("Summarize this research paper's contribution", "research.summarizer"),
        ("Write a short science fiction story about a lighthouse", "creative.story-writer"),
        ("Design a poster image for our college fest", "creative.poster-image"),
    ]
    from app.agents.router import get_router  # noqa: PLC0415 - needs app settings loaded

    router_agent = get_router()
    correct = 0
    for request_text, expected in routing_cases:
        decision = router_agent.route(request_text)
        ok = decision.agent_key == expected
        correct += int(ok)
        check(
            f"route → {expected}",
            ok,
            f"got {decision.agent_key} ({decision.source}, {decision.confidence:.2f})",
        )
    print(f"  · routing accuracy: {correct}/{len(routing_cases)}")

    auto = send(client, headers, "Why is my SQL LEFT JOIN returning duplicate rows?")
    check("chat without explicit agent -> 200", auto.status_code == 200)
    check(
        "router selected a technical agent end-to-end",
        auto.json()["routing"]["agent_key"].startswith("technical."),
        f"{auto.json()['routing']['agent_key']} ({auto.json()['routing']['source']})",
    )

    section("12. Feedback becomes a learned memory")
    feedback1 = client.post(
        "/api/feedback",
        headers=headers,
        json={
            "message_id": body1["assistant_message"]["id"],
            "rating": -1,
            "feedback_text": "Please keep the working more concise.",
        },
    )
    check("POST /feedback -> 201", feedback1.status_code == 201, str(feedback1.status_code))
    fb1 = feedback1.json()
    check("feedback is scoped to the agent", fb1["feedback"]["agent_key"] == "education.class10-maths")
    check("feedback carries the domain", fb1["feedback"]["domain"] == "education")
    check(
        "feedback stored as a memory",
        len(fb1["memories_created"]) > 0,
        "; ".join(fb1["memories_created"])[:80],
    )
    check(
        "a single signal did not rewrite the profile",
        fb1["profile_updated"] is False,
    )

    search = client.get(
        "/api/memory/search",
        headers=headers,
        params={"q": "how much working should the solution show?", "agent_key": "education.class10-maths"},
    ).json()
    check(
        "semantic search retrieves the preference",
        any("concise" in m["content"].lower() for m in search),
        "; ".join(m["content"] for m in search)[:90],
    )

    feedback2 = client.post(
        "/api/feedback",
        headers=headers,
        json={
            "message_id": send(
                client,
                headers,
                "Find the roots of x squared minus 7x plus 12 equals 0",
                agent_key="education.class10-maths",
            ).json()["assistant_message"]["id"],
            "rating": -1,
            "feedback_text": "Still too long — keep it concise please.",
        },
    ).json()
    check("repeated signal updated a profile", feedback2["profile_updated"] is True, str(feedback2["profile_changes"]))
    global_profile = client.get("/api/profile/global", headers=headers).json()
    check(
        "global profile now prefers concise responses",
        global_profile["preferred_response_length"] == "concise",
        global_profile["preferred_response_length"],
    )

    section("13. Memory scope isolation across agents and domains")
    taught = client.post(
        "/api/memory",
        headers=headers,
        json={
            "content": "Always label the diagram axes in maths answers",
            "agent_key": "education.class10-maths",
            "kind": "preference",
            "importance": 0.8,
        },
    )
    check("POST /memory (agent scope) -> 201", taught.status_code == 201)
    check(
        "memory records both agent_key and domain",
        taught.json()["agent_key"] == "education.class10-maths"
        and taught.json()["domain"] == "education",
        f"{taught.json()['agent_key']} / {taught.json()['domain']}",
    )
    domain_memory = client.post(
        "/api/memory",
        headers=headers,
        json={
            "content": "Prefers CBSE terminology in every subject",
            "domain": "education",
            "kind": "preference",
            "importance": 0.7,
        },
    )
    check(
        "domain-scoped memory has no agent_key",
        domain_memory.json()["agent_key"] is None
        and domain_memory.json()["domain"] == "education",
    )
    global_memory = client.post(
        "/api/memory",
        headers=headers,
        json={"content": "Never use emoji", "kind": "preference", "importance": 0.9},
    )
    check(
        "global memory has neither scope",
        global_memory.json()["agent_key"] is None and global_memory.json()["domain"] is None,
    )

    put_domain_profile(
        client,
        headers,
        "technical",
        {
            "experience": "3-5 years",
            "explanation_style": ["Runnable example first", "Type annotations"],
            "project_context": "FastAPI + React platform",
        },
    )
    put_agent_profile(
        client,
        headers,
        "technical.python",
        {"python_version": "3.12", "frameworks": ["FastAPI"], "level": "Advanced"},
    )
    tech_chat = send(
        client,
        headers,
        "Explain Python decorators with functools.wraps",
        agent_key="technical.python",
    )
    check("technical chat -> 200", tech_chat.status_code == 200)
    used = [m["content"].lower() for m in tech_chat.json()["personalization"]["memories_used"]]
    scopes = {m["scope"] for m in tech_chat.json()["personalization"]["memories_used"]}
    check(
        "maths-scoped memory did not leak into the Python agent",
        not any("diagram axes" in content for content in used),
        "; ".join(used)[:100],
    )
    check(
        "education-domain memory did not leak either",
        not any("cbse" in content for content in used),
        "; ".join(used)[:100],
    )
    check(
        "only global/technical scopes were used",
        scopes <= {"global", "technical", "technical.python"},
        ", ".join(sorted(scopes)) or "(none)",
    )
    agent_summary = " ".join(tech_chat.json()["personalization"]["agent_profile_summary"]).lower()
    check(
        "the Python agent's own profile was used",
        "fastapi" in agent_summary or "3.12" in agent_summary,
        agent_summary[:90],
    )

    summary = client.get("/api/memory/summary", headers=headers).json()
    check(
        "memory summary groups by agent and by domain",
        summary["total"] >= 3 and bool(summary["by_domain"]),
        f"total={summary['total']} by_domain={summary['by_domain']}",
    )
    check(
        "DELETE /memory/{id} -> 204",
        client.delete(f"/api/memory/{global_memory.json()['id']}", headers=headers).status_code
        == 204,
    )

    section("14. Streaming")
    stream = client.post(
        "/api/chat/stream",
        headers=headers,
        json={
            "message": "In one line, what is the quadratic formula?",
            "agent_key": "education.class10-maths",
        },
    )
    check("POST /chat/stream -> 200", stream.status_code == 200)
    events = sse_events(stream.text)
    names = [name for name, _ in events]
    check("meta event sent before generation", names and names[0] == "meta", ", ".join(names[:3]))
    check("delta events streamed", names.count("delta") >= 1, f"{names.count('delta')} deltas")
    check("done event closes the stream", names[-1] == "done", names[-1])
    meta = next(data for name, data in events if name == "meta")
    check("meta says streaming is on for a text agent", meta["streaming"] is True)
    done = next(data for name, data in events if name == "done")
    check("done carries the persisted message", bool(done["assistant_message"]["id"]))

    image_stream = client.post(
        "/api/chat/stream",
        headers=headers,
        json={
            "message": "Instagram square graphic announcing our new pricing",
            "agent_key": "marketing.post-image",
        },
    )
    ievents = sse_events(image_stream.text)
    inames = [name for name, _ in ievents]
    imeta = next(data for name, data in ievents if name == "meta")
    check("visual agent reports streaming=false", imeta["streaming"] is False)
    check("visual agent reports its output kind", imeta["output_kind"] == "image")
    check("a status event replaces token streaming", "status" in inames, ", ".join(inames))
    idone = next(data for name, data in ievents if name == "done")
    check(
        "streamed image delivered in the done event",
        len(idone["assistant_message"]["media"]) == 1
        and idone["assistant_message"]["output_kind"] == "image",
        str(idone["assistant_message"]["output_kind"]),
    )

    section("15. Conversations are keyed by agent and filterable by domain")
    conversations = client.get("/api/conversations", headers=headers).json()
    check("GET /conversations lists history", len(conversations) >= 4, str(len(conversations)))
    check(
        "every conversation carries agent_key + domain",
        all(c["agent_key"] and c["domain"] for c in conversations),
    )
    by_domain = client.get(
        "/api/conversations", headers=headers, params={"domain": "education"}
    ).json()
    check(
        "filter by domain works",
        by_domain and all(c["domain"] == "education" for c in by_domain),
        f"{len(by_domain)} education conversations",
    )
    by_agent = client.get(
        "/api/conversations", headers=headers, params={"agent_key": "marketing.post-image"}
    ).json()
    check(
        "filter by agent key works",
        by_agent and all(c["agent_key"] == "marketing.post-image" for c in by_agent),
        f"{len(by_agent)} post-image conversations",
    )

    detail_resp = client.get(f"/api/conversations/{maths_conversation}", headers=headers)
    check("GET /conversations/{id} -> 200", detail_resp.status_code == 200)
    detail_body = detail_resp.json()
    check(
        "conversation contains the persisted turn",
        len(detail_body["messages"]) == 2
        and detail_body["messages"][0]["role"] == "user"
        and detail_body["messages"][1]["role"] == "assistant",
        f"{len(detail_body['messages'])} messages",
    )
    check(
        "feedback rating is attached to the message",
        detail_body["messages"][1]["feedback_rating"] == -1,
    )
    image_conversation = by_agent[0]["id"]
    image_detail = client.get(f"/api/conversations/{image_conversation}", headers=headers).json()
    check(
        "media survives a reload from the database",
        any(m["media"] for m in image_detail["messages"]),
    )
    renamed = client.patch(
        f"/api/conversations/{maths_conversation}",
        headers=headers,
        json={"title": "Quadratic roots"},
    )
    check("rename conversation", renamed.json()["title"] == "Quadratic roots")
    continued = send(
        client,
        headers,
        "Now verify both roots by substitution.",
        conversation_id=maths_conversation,
        agent_key="education.class10-maths",
    )
    check("continue an existing conversation", continued.status_code == 200)
    check(
        "short-term memory carried the previous turns",
        continued.json()["personalization"]["short_term_messages"] >= 2,
        str(continued.json()["personalization"]["short_term_messages"]),
    )

    section("16. Attachments feed the data agents")
    upload = client.post(
        "/api/chat/upload",
        headers=headers,
        files={
            "file": (
                "sales.csv",
                b"month,amount\nJan,1200\nFeb,1500\nMar,1800\n",
                "text/csv",
            )
        },
    )
    check("POST /chat/upload -> 200", upload.status_code == 200)
    attachment = upload.json()
    with_file = send(
        client,
        headers,
        "Chart the monthly amounts from this file",
        agent_key="analytics.chart-builder",
        attachment_name=attachment["name"],
        attachment_text=attachment["text"],
    )
    check("chat with attachment -> 200", with_file.status_code == 200)
    check(
        "attachment characters were counted into the context",
        attachment["characters"] > 0
        and with_file.json()["personalization"]["context_characters"] > 0,
        f"{attachment['characters']} chars",
    )
    check(
        "unsupported upload type rejected (415)",
        client.post(
            "/api/chat/upload",
            headers=headers,
            files={"file": ("x.exe", b"MZ", "application/octet-stream")},
        ).status_code
        == 415,
    )

    section("17. Profile overview and dashboard counts")
    overview_resp = client.get("/api/profile/overview", headers=headers).json()
    check(
        "overview lists every domain slot",
        set(overview_resp["domain_profiles"]) == set(DOMAIN_ORDER),
        f"{len(overview_resp['domain_profiles'])} slots",
    )
    check(
        "overview lists every agent slot",
        len(overview_resp["agent_profiles"]) == len(AGENTS),
        str(len(overview_resp["agent_profiles"])),
    )
    check(
        "configured domains are filled in, others are null",
        overview_resp["domain_profiles"]["education"] is not None
        and overview_resp["domain_profiles"]["creative"] is None,
    )

    stats = client.get("/api/dashboard/stats", headers=headers).json()
    check("dashboard counts 7 domains", stats["total_domains"] == 7)
    check(
        f"dashboard counts {len(AGENTS)} agents",
        stats["total_agents"] == len(AGENTS),
        str(stats["total_agents"]),
    )
    check(
        "dashboard counts generated images/charts",
        stats["images_generated"] >= 2,
        str(stats["images_generated"]),
    )
    check(
        "dashboard counts configured domains",
        stats["configured_domains"] >= 3,
        str(stats["configured_domains"]),
    )

    domains_after = client.get("/api/domains", headers=headers).json()
    education_card = next(d for d in domains_after if d["key"] == "education")
    check(
        "education card now shows configured agents and activity",
        education_card["configured_agents"] >= 1 and education_card["conversation_count"] >= 1,
        f"configured={education_card['configured_agents']} "
        f"conversations={education_card['conversation_count']}",
    )
    check(
        "education card is marked Personalized",
        education_card["status_label"] == "Personalized",
        education_card["status_label"],
    )

    section("18. Tenant isolation")
    other = client.post(
        "/api/auth/register",
        json={
            "name": "Other User",
            "email": f"other+{uuid.uuid4().hex[:8]}@example.com",
            "password": "OtherPass123",
        },
    ).json()
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}
    check(
        "another user cannot read this conversation",
        client.get(
            f"/api/conversations/{maths_conversation}", headers=other_headers
        ).status_code
        == 404,
    )
    check(
        "another user sees no memories",
        client.get("/api/memory", headers=other_headers).json() == [],
    )
    check(
        "another user's agents are all unconfigured",
        all(
            a["status_label"] == "Not configured"
            for a in client.get("/api/agents", headers=other_headers).json()
        ),
    )
    check(
        "another user's image count is zero",
        client.get("/api/dashboard/stats", headers=other_headers).json()["images_generated"] == 0,
    )

    section("19. Cleanup")
    check(
        "DELETE /conversations/{id} -> 204",
        client.delete(f"/api/conversations/{maths_conversation}", headers=headers).status_code
        == 204,
    )
    check(
        "deleted conversation is gone",
        client.get(f"/api/conversations/{maths_conversation}", headers=headers).status_code == 404,
    )

    print("\n" + "=" * 68)
    print(f"\033[1mPASSED: {len(PASSED)}   FAILED: {len(FAILED)}\033[0m")
    if FAILED:
        print("\nFailures:")
        for label in FAILED:
            print(f"  - {label}")
    print("=" * 68)
    return 1 if FAILED else 0


if __name__ == "__main__":
    os.environ.setdefault("APP_ENV", "development")
    raise SystemExit(main())
