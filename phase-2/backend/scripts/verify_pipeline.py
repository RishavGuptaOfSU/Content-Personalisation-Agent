#!/usr/bin/env python
"""End-to-end verification of the marketing agent platform.

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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app.agents.catalog import AGENTS, image_agents, list_agents  # noqa: E402
from app.agents.definitions import PRIMARY_DOMAIN  # noqa: E402
from app.main import app  # noqa: E402
from app.media import media_root  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []

EXPECTED_AGENTS = {
    "marketing.post-image",
    "marketing.ad-creative",
    "marketing.social-copy",
    "marketing.seo-optimizer",
    "marketing.campaign-planner",
}

BRAND = {
    "brand_name": "Acme Cloud",
    "industry": "SaaS / Software",
    "audience": ["Developers", "Founders"],
    "tone": "Professional",
    "brand_colors": "#4F46E5, #0F172A",
    "avoid": ["clickbait", "emojis"],
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


# --------------------------------------------------------------------- helpers
def put_brand(client: TestClient, headers: dict, data: dict) -> object:
    return client.put(
        f"/api/profile/domain/{PRIMARY_DOMAIN}", headers=headers, json={"profile_data": data}
    )


def put_agent_profile(client: TestClient, headers: dict, agent_key: str, data: dict) -> object:
    return client.put(
        f"/api/profile/agent/{agent_key}", headers=headers, json={"profile_data": data}
    )


def send(client: TestClient, headers: dict, message: str, **kwargs) -> object:
    payload: dict = {"message": message}
    payload.update(kwargs)
    return client.post("/api/chat", headers=headers, json=payload)


def sse_events(raw: str) -> list[tuple[str, object]]:
    events: list[tuple[str, object]] = []
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


def main() -> int:
    with TestClient(app) as client:
        return run_journey(client)


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
    print(
        f"  · LLM provider: {health['providers']['llm']['provider']} "
        f"({health['providers']['llm']['model']})"
    )

    section("1. Catalog shape: one domain, five narrow agents")
    overview = client.get("/api/catalog").json()
    check("exactly one domain", overview["domains"] == 1, str(overview["domains"]))
    check("five agents", overview["agents"] == 5, str(overview["agents"]))
    check(
        "agent count matches the catalog module",
        overview["agents"] == len(AGENTS),
        f"{len(AGENTS)} in catalog",
    )
    check(
        "two image agents, three text agents",
        overview["output_kinds"]["image"] == 2 and overview["output_kinds"]["text"] == 3,
        str(overview["output_kinds"]),
    )
    check(
        "the image agents are post-image and ad-creative",
        set(overview["image_agents"]) == {"marketing.post-image", "marketing.ad-creative"},
        ", ".join(sorted(overview["image_agents"])),
    )
    check(
        "every agent key is in the marketing domain",
        {spec.key for spec in list_agents()} == EXPECTED_AGENTS,
        ", ".join(sorted(spec.key for spec in list_agents())),
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

    section("3. The agent list is the landing surface")
    agents = client.get("/api/agents", headers=headers)
    check("GET /agents -> 200", agents.status_code == 200)
    agent_list = agents.json()
    check("five agent cards", len(agent_list) == 5, f"{len(agent_list)} agents")
    check(
        "all five start unconfigured",
        all(a["status_label"] == "Not configured" for a in agent_list),
    )
    check(
        "the visual agents advertise their output kind",
        {a["key"] for a in agent_list if a["output_kind"] == "image"}
        == {"marketing.post-image", "marketing.ad-creative"},
    )
    check(
        "unknown agent -> 404",
        client.get("/api/agents/marketing.nope", headers=headers).status_code == 404,
    )
    domain_card = client.get(f"/api/domains/{PRIMARY_DOMAIN}", headers=headers)
    check("the brand domain is still addressable", domain_card.status_code == 200)
    check(
        "it reports five agents",
        domain_card.json()["agent_count"] == 5,
        str(domain_card.json()["agent_count"]),
    )
    check(
        "unknown domain -> 404",
        client.get("/api/domains/education", headers=headers).status_code == 404,
    )

    section("4. Agent detail carries both setup forms")
    detail = client.get("/api/agents/marketing.social-copy", headers=headers).json()
    check("output_kind is text", detail["output_kind"] == "text")
    check("scope sentence present", "copy" in detail["scope"].lower(), detail["scope"][:60])
    check(
        "out_of_scope points at the image agents",
        any("image" in item.lower() for item in detail["out_of_scope"]),
        "; ".join(detail["out_of_scope"])[:90],
    )
    check(
        "the brand form asks the shared questions",
        "brand_name" in [f["key"] for f in detail["domain_profile_fields"]],
        ", ".join(f["key"] for f in detail["domain_profile_fields"]),
    )
    check(
        "the agent form asks only its own questions",
        {"platforms", "length", "use_hashtags"} == {f["key"] for f in detail["profile_fields"]},
        ", ".join(f["key"] for f in detail["profile_fields"]),
    )
    check("needs_setup is true before setup", detail["needs_setup"] is True)

    section("5. Two-level setup: brand profile, then agent profile")
    brand_saved = put_brand(client, headers, BRAND)
    check("PUT /profile/domain/marketing -> 200", brand_saved.status_code == 200)
    check("brand profile marked configured", brand_saved.json()["is_configured"] is True)

    still_needs = client.get("/api/profile/agent/marketing.social-copy", headers=headers).json()
    check(
        "agent still needs its own setup after the brand step",
        still_needs["domain_configured"] is True and still_needs["agent_configured"] is False,
        f"brand={still_needs['domain_configured']} agent={still_needs['agent_configured']}",
    )

    agent_saved = put_agent_profile(
        client,
        headers,
        "marketing.social-copy",
        {"platforms": ["LinkedIn"], "length": "Short (50-120)", "use_hashtags": "Yes, a few"},
    )
    check("PUT /profile/agent/marketing.social-copy -> 200", agent_saved.status_code == 200)
    check("agent profile marked configured", agent_saved.json()["is_configured"] is True)
    status = client.get("/api/profile/agent/marketing.social-copy", headers=headers).json()
    check("needs_setup is now false", status["needs_setup"] is False)
    check("status label is Personalized", status["status_label"] == "Personalized")

    sibling = client.get("/api/profile/agent/marketing.seo-optimizer", headers=headers).json()
    check(
        "a sibling agent reuses the brand profile but needs its own setup",
        sibling["domain_configured"] is True and sibling["agent_configured"] is False,
    )

    section("6. Chat with a text agent")
    chat1 = send(
        client,
        headers,
        "Write a LinkedIn post about how much cloud spend sits idle",
        agent_key="marketing.social-copy",
    )
    check("POST /chat -> 200", chat1.status_code == 200, str(chat1.status_code))
    if chat1.status_code != 200:
        print(chat1.text)
        return 1
    body1 = chat1.json()
    copy_conversation = body1["conversation_id"]
    check(
        "explicit selection overrode the router",
        body1["routing"]["agent_key"] == "marketing.social-copy"
        and body1["routing"]["source"] == "explicit",
        body1["routing"]["source"],
    )
    check("routing reports the domain", body1["routing"]["domain"] == PRIMARY_DOMAIN)
    check("request judged in scope", body1["scope"]["in_scope"] is True)
    check("assistant produced text", body1["assistant_message"]["output_kind"] == "text")
    check("assistant message has no media", body1["assistant_message"]["media"] == [])
    check(
        "the brand name reached the context",
        any("Acme Cloud" in line for line in body1["personalization"]["domain_profile_summary"]),
        "; ".join(body1["personalization"]["domain_profile_summary"])[:90],
    )
    check(
        "the agent's own platform choice reached the context",
        any("LinkedIn" in line for line in body1["personalization"]["agent_profile_summary"]),
        "; ".join(body1["personalization"]["agent_profile_summary"])[:90],
    )
    check(
        "the prompt carries the scope contract",
        "YOUR SCOPE" in body1["personalization"]["system_prompt_preview"],
        body1["personalization"]["system_prompt_preview"][:60],
    )

    section("7. Scope guard hands off between siblings")
    handoff = send(
        client,
        headers,
        "Create the post image graphic for our launch announcement",
        agent_key="marketing.social-copy",
    )
    check("out-of-scope request still -> 200", handoff.status_code == 200)
    hbody = handoff.json()
    check("scope.in_scope is false", hbody["scope"]["in_scope"] is False, hbody["scope"]["reason"])
    check(
        "handed off to the image agent",
        hbody["scope"]["suggested_agent_key"] == "marketing.post-image",
        str(hbody["scope"]["suggested_agent_key"]),
    )
    check(
        "the reply names the agent that should handle it",
        (hbody["scope"]["suggested_agent_name"] or "") in hbody["assistant_message"]["content"],
        hbody["assistant_message"]["content"][:80].replace("\n", " "),
    )
    check(
        "no model call was spent on the handoff",
        hbody["assistant_message"]["meta"]["provider"] == "scope-guard",
        str(hbody["assistant_message"]["meta"]["provider"]),
    )
    check(
        "an in-scope short greeting is NOT handed off",
        send(client, headers, "hello", agent_key="marketing.social-copy").json()["scope"][
            "in_scope"
        ]
        is True,
    )

    section("8. Post image agent returns a rendered graphic, not prose")
    put_agent_profile(
        client,
        headers,
        "marketing.post-image",
        {"platform": "LinkedIn", "style": "Bold type", "include_logo_text": "ACME CLOUD"},
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
    message = image_chat.json()["assistant_message"]
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
        check("alt text produced for accessibility", bool(media["alt_text"]), media["alt_text"][:60])
        on_disk = media_root() / media["filename"]
        check("file exists on disk", on_disk.is_file(), str(on_disk))
        if on_disk.is_file():
            check(
                "file really is a PNG",
                on_disk.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),
            )
            check(
                "reported byte size matches the file",
                media["bytes"] == on_disk.stat().st_size,
                f"{media['bytes']} vs {on_disk.stat().st_size}",
            )
        served = client.get(media["url"])
        check("GET the media url -> 200", served.status_code == 200, str(served.status_code))
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
        "no image agent is streamable",
        all(spec.output_kind.value != "text" for spec in image_agents()),
    )
    check(
        "traversal on the media route refused",
        client.get("/api/media/..%2f..%2fapp%2fmain.py").status_code in (400, 404),
    )

    section("9. Ad creative renders at its own ad size")
    put_agent_profile(
        client,
        headers,
        "marketing.ad-creative",
        {"objective": "Free trial signups", "size": "Square 1080x1080"},
    )
    ad_chat = send(
        client,
        headers,
        "Ad creative promoting our free trial for engineering teams",
        agent_key="marketing.ad-creative",
    )
    check("ad chat -> 200", ad_chat.status_code == 200, str(ad_chat.status_code))
    ad_message = ad_chat.json()["assistant_message"]
    check("output_kind is image", ad_message["output_kind"] == "image")
    if ad_message["media"]:
        ad_media = ad_message["media"][0]
        check(
            "the ad size from the agent profile was used",
            (ad_media["width"], ad_media["height"]) == (1080, 1080),
            f"{ad_media['width']}x{ad_media['height']}",
        )
        check(
            "the two image agents produced different files",
            ad_media["filename"] != (message["media"][0]["filename"] if message["media"] else ""),
        )
        check("renderer recorded", bool(ad_media["renderer"]), ad_media["renderer"])

    section("10. Router picks the right agent with no explicit selection")
    routing_cases = [
        ("Write an Instagram caption for our launch", "marketing.social-copy"),
        ("Write ad copy for our free trial", "marketing.social-copy"),
        ("Create a LinkedIn post image about AI automation", "marketing.post-image"),
        ("Make a promotional graphic for our webinar", "marketing.post-image"),
        ("Design an ad creative for our free trial", "marketing.ad-creative"),
        ("Google display ad promoting 30% off annual plans", "marketing.ad-creative"),
        ("Title tag and meta description for our pricing page", "marketing.seo-optimizer"),
        ("Keyword research for a blog about DevOps", "marketing.seo-optimizer"),
        ("Plan a two week multi-channel launch campaign", "marketing.campaign-planner"),
        ("Build me a content calendar for next month", "marketing.campaign-planner"),
    ]
    from app.agents.router import get_router  # noqa: PLC0415 - needs settings loaded

    router_agent = get_router()
    correct = 0
    for request_text, expected in routing_cases:
        decision = router_agent.route(request_text)
        ok = decision.agent_key == expected
        correct += int(ok)
        check(
            f"route → {expected.split('.')[-1]}",
            ok,
            f"got {decision.agent_key.split('.')[-1]} ({decision.source}, {decision.confidence:.2f})",
        )
    print(f"  · routing accuracy: {correct}/{len(routing_cases)}")

    check(
        "an unclassifiable request stays inside the domain",
        router_agent.route("Make something for us").agent_key.startswith("marketing."),
        router_agent.route("Make something for us").agent_key,
    )

    auto = send(client, headers, "Title tag and meta description for our pricing page")
    check("chat without explicit agent -> 200", auto.status_code == 200)
    check(
        "router selected the SEO agent end-to-end",
        auto.json()["routing"]["agent_key"] == "marketing.seo-optimizer",
        f"{auto.json()['routing']['agent_key']} ({auto.json()['routing']['source']})",
    )

    section("11. Feedback becomes a learned memory, then a profile change")
    feedback1 = client.post(
        "/api/feedback",
        headers=headers,
        json={
            "message_id": body1["assistant_message"]["id"],
            "rating": -1,
            "feedback_text": "Please keep the posts more concise.",
        },
    )
    check("POST /feedback -> 201", feedback1.status_code == 201, str(feedback1.status_code))
    fb1 = feedback1.json()
    check(
        "feedback is scoped to the agent",
        fb1["feedback"]["agent_key"] == "marketing.social-copy",
    )
    check("feedback carries the domain", fb1["feedback"]["domain"] == PRIMARY_DOMAIN)
    check(
        "feedback stored as a memory",
        len(fb1["memories_created"]) > 0,
        "; ".join(fb1["memories_created"])[:70],
    )
    check("a single signal did not rewrite the profile", fb1["profile_updated"] is False)

    search = client.get(
        "/api/memory/search",
        headers=headers,
        params={"q": "how long should the posts be?", "agent_key": "marketing.social-copy"},
    ).json()
    check(
        "semantic search retrieves the preference",
        any("concise" in m["content"].lower() for m in search),
        "; ".join(m["content"] for m in search)[:80],
    )

    feedback2 = client.post(
        "/api/feedback",
        headers=headers,
        json={
            "message_id": send(
                client,
                headers,
                "Another LinkedIn post, this time about idle staging environments",
                agent_key="marketing.social-copy",
            ).json()["assistant_message"]["id"],
            "rating": -1,
            "feedback_text": "Still too long — keep it concise please.",
        },
    ).json()
    check(
        "repeated signal updated a profile",
        feedback2["profile_updated"] is True,
        str(feedback2["profile_changes"]),
    )
    global_profile = client.get("/api/profile/global", headers=headers).json()
    check(
        "global profile now prefers concise responses",
        global_profile["preferred_response_length"] == "concise",
        global_profile["preferred_response_length"],
    )

    section("12. Memory scope isolation between sibling agents")
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
    check("POST /memory (agent scope) -> 201", taught.status_code == 201)
    check(
        "memory records both agent_key and domain",
        taught.json()["agent_key"] == "marketing.social-copy"
        and taught.json()["domain"] == PRIMARY_DOMAIN,
        f"{taught.json()['agent_key']} / {taught.json()['domain']}",
    )
    brand_memory = client.post(
        "/api/memory",
        headers=headers,
        json={
            "content": "Positions on engineering time saved, never on price",
            "domain": PRIMARY_DOMAIN,
            "kind": "requirement",
            "importance": 0.8,
        },
    )
    check(
        "brand-wide memory has no agent_key",
        brand_memory.json()["agent_key"] is None
        and brand_memory.json()["domain"] == PRIMARY_DOMAIN,
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

    seo_chat = send(
        client,
        headers,
        "Optimise the title and meta for our cloud cost automation landing page",
        agent_key="marketing.seo-optimizer",
    )
    check("sibling agent chat -> 200", seo_chat.status_code == 200)
    used = [m["content"].lower() for m in seo_chat.json()["personalization"]["memories_used"]]
    scopes = {m["scope"] for m in seo_chat.json()["personalization"]["memories_used"]}
    check(
        "the caption-specific memory did not leak into the SEO agent",
        not any("end captions with a question" in content for content in used),
        "; ".join(used)[:90],
    )
    check(
        "only global / brand / own-agent scopes were used",
        scopes <= {"global", PRIMARY_DOMAIN, "marketing.seo-optimizer"},
        ", ".join(sorted(scopes)) or "(none)",
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

    section("13. Streaming")
    stream = client.post(
        "/api/chat/stream",
        headers=headers,
        json={
            "message": "One line of copy for our pricing page",
            "agent_key": "marketing.social-copy",
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

    section("14. Conversations")
    conversations = client.get("/api/conversations", headers=headers).json()
    check("GET /conversations lists history", len(conversations) >= 4, str(len(conversations)))
    check(
        "every conversation carries agent_key + domain",
        all(c["agent_key"] and c["domain"] for c in conversations),
    )
    by_agent = client.get(
        "/api/conversations", headers=headers, params={"agent_key": "marketing.post-image"}
    ).json()
    check(
        "filter by agent key works",
        by_agent and all(c["agent_key"] == "marketing.post-image" for c in by_agent),
        f"{len(by_agent)} post-image conversations",
    )

    detail_resp = client.get(f"/api/conversations/{copy_conversation}", headers=headers)
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
    image_detail = client.get(f"/api/conversations/{by_agent[0]['id']}", headers=headers).json()
    check(
        "media survives a reload from the database",
        any(m["media"] for m in image_detail["messages"]),
    )
    renamed = client.patch(
        f"/api/conversations/{copy_conversation}",
        headers=headers,
        json={"title": "Idle cloud spend post"},
    )
    check("rename conversation", renamed.json()["title"] == "Idle cloud spend post")
    continued = send(
        client,
        headers,
        "Now shorten it to two sentences.",
        conversation_id=copy_conversation,
        agent_key="marketing.social-copy",
    )
    check("continue an existing conversation", continued.status_code == 200)
    check(
        "short-term memory carried the previous turns",
        continued.json()["personalization"]["short_term_messages"] >= 2,
        str(continued.json()["personalization"]["short_term_messages"]),
    )

    section("15. Attachments feed the text agents")
    upload = client.post(
        "/api/chat/upload",
        headers=headers,
        files={
            "file": (
                "landing.md",
                b"# Acme Cloud\nFind idle cloud capacity automatically.\n"
                b"Trusted by engineering teams.\n",
                "text/markdown",
            )
        },
    )
    check("POST /chat/upload -> 200", upload.status_code == 200)
    attachment = upload.json()
    with_file = send(
        client,
        headers,
        "Optimise this landing page copy for search",
        agent_key="marketing.seo-optimizer",
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

    section("16. Profile overview and dashboard counts")
    overview_resp = client.get("/api/profile/overview", headers=headers).json()
    check(
        "overview has the single domain slot",
        set(overview_resp["domain_profiles"]) == {PRIMARY_DOMAIN},
        ", ".join(overview_resp["domain_profiles"]),
    )
    check(
        "overview lists all five agent slots",
        len(overview_resp["agent_profiles"]) == 5,
        str(len(overview_resp["agent_profiles"])),
    )
    check(
        "the brand profile is filled in",
        overview_resp["domain_profiles"][PRIMARY_DOMAIN] is not None,
    )

    stats = client.get("/api/dashboard/stats", headers=headers).json()
    check("dashboard counts one domain", stats["total_domains"] == 1)
    check("dashboard counts five agents", stats["total_agents"] == 5, str(stats["total_agents"]))
    check(
        "dashboard counts generated images",
        stats["images_generated"] >= 3,
        str(stats["images_generated"]),
    )
    check(
        "dashboard counts configured agents",
        stats["configured_agents"] >= 3,
        str(stats["configured_agents"]),
    )

    section("17. Tenant isolation")
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
            f"/api/conversations/{copy_conversation}", headers=other_headers
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
        "another user's brand profile is empty",
        client.get(f"/api/profile/domain/{PRIMARY_DOMAIN}", headers=other_headers).json()
        in (None, {}),
    )
    check(
        "another user's image count is zero",
        client.get("/api/dashboard/stats", headers=other_headers).json()["images_generated"] == 0,
    )

    section("18. Cleanup")
    check(
        "DELETE /conversations/{id} -> 204",
        client.delete(f"/api/conversations/{copy_conversation}", headers=headers).status_code
        == 204,
    )
    check(
        "deleted conversation is gone",
        client.get(f"/api/conversations/{copy_conversation}", headers=headers).status_code == 404,
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
