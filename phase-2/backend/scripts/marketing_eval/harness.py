#!/usr/bin/env python
"""Run the marketing evaluation dataset and write a comparable report.

Two halves, deliberately kept apart:

* **Deterministic** — things a machine can decide: routing target, scope
  handoff, output kind, media dimensions, whether the image spec came from the
  model or the degraded fallback, hashtag counts, length bounds, whether the
  profile and memories actually reached the prompt, and substring checks for
  fabricated figures. These pass or fail.
* **Qualitative** — hook quality, brand fit, usefulness. The harness does *not*
  score these. It writes the real output into a markdown report next to the
  rubric dimensions each case declares, for a human to score. String matching
  is not a measure of creative quality and is not presented as one.

    python scripts/marketing_eval/harness.py                      # everything
    python scripts/marketing_eval/harness.py --agent social-copy
    python scripts/marketing_eval/harness.py --category grounding
    python scripts/marketing_eval/harness.py --no-generate         # routing/scope only
    python scripts/marketing_eval/harness.py --label baseline

Every report records the provider, model and the settings that affect output, so
two runs are only compared when they were produced the same way.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import tomllib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parents[1]
sys.path.insert(0, str(BACKEND))

os.environ.setdefault("APP_ENV", "development")

from fastapi.testclient import TestClient  # noqa: E402

from app.agents.definitions import PRIMARY_DOMAIN  # noqa: E402
from app.agents.router import get_router  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.media import media_root  # noqa: E402

CASES_FILE = HERE / "cases.toml"
REPORT_DIR = HERE / "reports"

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
        "channels": ["LinkedIn", "Email", "Blog / SEO"],
        "budget": "Small (<$500/mo)",
    },
}
#: Memories seeded so `memory_must_apply` cases have something to retrieve.
SEED_MEMORIES = [
    {
        "content": "Wants LinkedIn posts kept under 100 words",
        "agent_key": "marketing.social-copy",
        "kind": "preference",
        "importance": 0.8,
    },
    {
        "content": "Positions on engineering time saved, never on price",
        "domain": PRIMARY_DOMAIN,
        "kind": "requirement",
        "importance": 0.8,
    },
]

_HASHTAG_RE = re.compile(r"(?<!\w)#\w+")


@dataclass
class CaseResult:
    case_id: str
    agent: str
    category: str
    request: str
    #: (assertion, passed, detail)
    assertions: list[tuple[str, bool, str]] = field(default_factory=list)
    content: str = ""
    media: list[dict[str, Any]] = field(default_factory=list)
    scope: dict[str, Any] = field(default_factory=dict)
    routing: dict[str, Any] = field(default_factory=dict)
    rubric: list[str] = field(default_factory=list)
    latency_ms: int = 0
    skipped: str | None = None
    error: str | None = None

    def add(self, label: str, ok: bool, detail: str = "") -> None:
        self.assertions.append((label, bool(ok), detail))

    @property
    def failures(self) -> list[tuple[str, bool, str]]:
        return [a for a in self.assertions if not a[1]]

    @property
    def passed(self) -> int:
        return sum(1 for a in self.assertions if a[1])


def load_cases() -> list[dict[str, Any]]:
    return tomllib.loads(CASES_FILE.read_text(encoding="utf-8"))["case"]


def run_configuration() -> dict[str, Any]:
    """Everything that can change the output, recorded with each report."""
    model_for_provider = {
        "ollama": getattr(settings, "OLLAMA_MODEL", None),
        "openai": getattr(settings, "OPENAI_MODEL", None),
        "bedrock": getattr(settings, "BEDROCK_MODEL_ID", None),
        "nemotron": getattr(settings, "NEMOTRON_MODEL", None),
        "mock": "local-dev-composer",
    }
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": model_for_provider.get(settings.LLM_PROVIDER, "unknown"),
        # Per-agent overrides, so a mixed fleet is distinguishable from a
        # single-model run. Without this a report cannot prove which model
        # actually answered which case.
        "agent_models": dict(settings.AGENT_MODELS),
        "llm_temperature": settings.LLM_TEMPERATURE,
        "llm_max_tokens": settings.LLM_MAX_TOKENS,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "embedding_dim": settings.EMBEDDING_DIM,
        "memory_min_similarity": settings.MEMORY_MIN_SIMILARITY,
        "image_provider": settings.IMAGE_PROVIDER,
        "router_use_llm": settings.ROUTER_USE_LLM,
        "scope_own_max_score": settings.SCOPE_OWN_MAX_SCORE,
        "scope_other_min_score": settings.SCOPE_OTHER_MIN_SCORE,
    }


# --------------------------------------------------------------- assertions
def assert_case(result: CaseResult, case: dict[str, Any], body: dict[str, Any]) -> None:
    message = body["assistant_message"]
    content = message["content"]
    media = message["media"]
    personalization = body["personalization"]

    result.content = content
    result.media = media
    result.scope = body.get("scope") or {}
    result.routing = body.get("routing") or {}
    result.latency_ms = body.get("latency_ms", 0)

    if "expect_output_kind" in case:
        result.add(
            f"output_kind == {case['expect_output_kind']}",
            message["output_kind"] == case["expect_output_kind"],
            message["output_kind"],
        )

    if case.get("expect_in_scope") is True:
        result.add("judged in scope", result.scope.get("in_scope") is True,
                   str(result.scope.get("reason", ""))[:70])

    if "media_size" in case and media:
        want = tuple(case["media_size"])
        got = (media[0]["width"], media[0]["height"])
        result.add(f"rendered at {want[0]}x{want[1]}", got == tuple(want), f"{got[0]}x{got[1]}")

    if case.get("expect_output_kind") == "image":
        result.add("a file was rendered", len(media) == 1, f"{len(media)} media items")
        if media:
            path = media_root() / media[0]["filename"]
            result.add(
                "the file is a real PNG on disk",
                path.is_file() and path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),
                str(path.name),
            )
            result.add("alt text present", bool(media[0]["alt_text"]), media[0]["alt_text"][:60])

    if case.get("require_spec_from_model"):
        degraded = message["meta"].get("incomplete_reason")
        result.add(
            "the image spec came from the model, not the fallback",
            not degraded,
            str(degraded or "")[:80],
        )

    for needle in case.get("profile_must_reach", []):
        haystack = " ".join(
            personalization.get("domain_profile_summary", [])
            + personalization.get("agent_profile_summary", [])
        )
        result.add(f"profile reached the prompt: {needle!r}", needle in haystack)

    if "memory_must_apply" in case:
        memories = " ".join(m["content"] for m in personalization.get("memories_used", []))
        result.add(
            f"memory retrieved: {case['memory_must_apply']!r}",
            case["memory_must_apply"].lower() in memories.lower(),
            memories[:70] or "(none retrieved)",
        )

    if "max_hashtags" in case:
        count = len(_HASHTAG_RE.findall(content))
        result.add(
            f"at most {case['max_hashtags']} hashtags", count <= case["max_hashtags"], str(count)
        )

    if "min_chars" in case:
        result.add(
            f"at least {case['min_chars']} chars", len(content) >= case["min_chars"], str(len(content))
        )
    if "max_chars" in case:
        result.add(
            f"at most {case['max_chars']} chars", len(content) <= case["max_chars"], str(len(content))
        )

    if "must_contain_any" in case:
        hit = next((n for n in case["must_contain_any"] if n.lower() in content.lower()), None)
        result.add(
            f"contains one of {case['must_contain_any']}", hit is not None, f"matched {hit!r}"
        )

    for needle in case.get("must_not_contain", []):
        # Image agents put their copy on the graphic, so check the spec too.
        # The grounding note is appended by the guard and legitimately quotes
        # the offending figure, so it is excluded from the search.
        body = content.split("⚠️ **Unverified figures:**")[0]
        surfaces = [body] + [json.dumps(m.get("spec") or {}) for m in media]
        present = any(needle.lower() in s.lower() for s in surfaces)
        result.add(f"does not contain {needle!r}", not present)

    if case.get("no_unsupported_figures"):
        flagged = message["meta"].get("unsupported_figures") or []
        result.add(
            "no figures the user did not supply",
            not flagged,
            ", ".join(flagged) or "none",
        )

    if "budget_allocations_sum_to" in case:
        want = float(case["budget_allocations_sum_to"])
        amounts = [
            float(value.replace(",", ""))
            for value in re.findall(r"[$₹€£]\s?(\d[\d,]*)", content)
        ]
        # The total may be restated alongside the split; drop it before summing.
        split = [value for value in amounts if value != want]
        total = sum(split)
        result.add(
            f"the allocations account for {want:g}",
            abs(total - want) < 0.01 or want in amounts,
            f"found {amounts} -> split sums to {total:g}",
        )


def assert_handoff(result: CaseResult, case: dict[str, Any], body: dict[str, Any]) -> None:
    scope = body.get("scope") or {}
    message = body["assistant_message"]
    result.scope = scope
    result.content = message["content"]
    result.routing = body.get("routing") or {}
    result.latency_ms = body.get("latency_ms", 0)

    result.add("judged out of scope", scope.get("in_scope") is False, str(scope.get("reason"))[:70])
    if "handoff_to" in case:
        result.add(
            f"handed off to {case['handoff_to'].split('.')[-1]}",
            scope.get("suggested_agent_key") == case["handoff_to"],
            str(scope.get("suggested_agent_key")),
        )
    result.add(
        "no model call was spent",
        message["meta"].get("provider") == "scope-guard",
        str(message["meta"].get("provider")),
    )
    name = scope.get("suggested_agent_name")
    if name:
        result.add("the reply names the right agent", name in message["content"])


def assert_routing(result: CaseResult, case: dict[str, Any]) -> None:
    decision = get_router().route(case["request"])
    result.routing = {
        "agent_key": decision.agent_key,
        "source": decision.source,
        "confidence": decision.confidence,
        "reason": decision.reason,
    }
    result.add(
        f"routes to {case['route_to'].split('.')[-1]}",
        decision.agent_key == case["route_to"],
        f"{decision.agent_key} ({decision.source}, {decision.confidence:.2f})",
    )
    result.add(
        "stayed inside the marketing domain",
        decision.agent_key.startswith(f"{PRIMARY_DOMAIN}."),
        decision.agent_key,
    )


# -------------------------------------------------------------------- report
def write_reports(
    results: list[CaseResult], config: dict[str, Any], label: str, elapsed: float
) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    provider = str(config.get("llm_provider"))
    base = f"{stamp}-{label}-{provider}"

    total = sum(len(r.assertions) for r in results)
    failed = sum(len(r.failures) for r in results)
    payload = {
        "label": label,
        "generated_at": stamp,
        "elapsed_seconds": round(elapsed, 1),
        "configuration": config,
        "totals": {
            "cases": len(results),
            "assertions": total,
            "passed": total - failed,
            "failed": failed,
            "errors": sum(1 for r in results if r.error),
            "skipped": sum(1 for r in results if r.skipped),
            "degraded_image_specs": sum(
                1
                for r in results
                if r.media and any("no usable JSON" in (r.error or "") for _ in [0])
            ),
        },
        "cases": [
            {
                "id": r.case_id,
                "agent": r.agent,
                "category": r.category,
                "request": r.request,
                "skipped": r.skipped,
                "error": r.error,
                "latency_ms": r.latency_ms,
                "assertions": [
                    {"label": a, "passed": p, "detail": d} for a, p, d in r.assertions
                ],
                "routing": r.routing,
                "scope": r.scope,
                "media": [
                    {k: m.get(k) for k in ("filename", "width", "height", "bytes", "alt_text", "spec")}
                    for m in r.media
                ],
                "rubric": r.rubric,
                "output": r.content,
            }
            for r in results
        ],
    }
    json_path = REPORT_DIR / f"{base}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ---- human-readable, for rubric scoring ----
    lines = [
        f"# Marketing evaluation — {label}",
        "",
        f"Generated {stamp} · {len(results)} cases · {elapsed:.0f}s",
        "",
        "## Configuration",
        "",
        "| setting | value |",
        "|---|---|",
        *[f"| `{k}` | {v} |" for k, v in config.items()],
        "",
        "## Deterministic results",
        "",
        f"**{total - failed}/{total} assertions passed** across {len(results)} cases.",
        "",
        "| case | agent | category | assertions | failures |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        state = (
            f"skipped ({r.skipped})"
            if r.skipped
            else (f"ERROR {r.error}" if r.error else f"{r.passed}/{len(r.assertions)}")
        )
        lines.append(
            f"| `{r.case_id}` | {r.agent.split('.')[-1] if r.agent else '—'} | {r.category} "
            f"| {state} | {len(r.failures)} |"
        )
    if failed:
        lines += ["", "### Failed assertions", ""]
        for r in results:
            for a, _p, d in r.failures:
                lines.append(f"- `{r.case_id}` — {a}" + (f" → {d}" if d else ""))

    lines += [
        "",
        "## Outputs for qualitative scoring",
        "",
        "Score each dimension 1–5 using `rubric.md`. The harness deliberately does",
        "not score these.",
        "",
    ]
    for r in results:
        if r.skipped or not (r.content or r.media):
            continue
        lines += [f"### `{r.case_id}` — {r.agent or 'routing'} ({r.category})", ""]
        lines += [f"**Request:** {r.request.strip()}", ""]
        if r.media:
            for m in r.media:
                lines += [
                    f"**Rendered:** `{m['filename']}` {m['width']}×{m['height']} "
                    f"({m.get('bytes', 0)} bytes)",
                    "",
                    f"**Alt text:** {m.get('alt_text', '')}",
                    "",
                    "**Spec from the model:**",
                    "",
                    "```json",
                    json.dumps(m.get("spec") or {}, indent=2),
                    "```",
                    "",
                ]
        if r.content:
            lines += ["**Reply:**", "", "```", r.content.strip(), "```", ""]
        if r.rubric:
            lines += [
                "**Score:** " + " · ".join(f"{dim} __/5" for dim in r.rubric),
                "",
            ]
        lines.append("---")
        lines.append("")

    md_path = REPORT_DIR / f"{base}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


# ---------------------------------------------------------------------- main
def main() -> int:  # noqa: PLR0915 - a linear runner
    parser = argparse.ArgumentParser(description="Run the marketing evaluation suite")
    parser.add_argument("--agent", help="Only cases for this agent (slug or full key)")
    parser.add_argument("--category", help="Only cases in this category")
    parser.add_argument("--id", help="Only this case id")
    parser.add_argument("--limit", type=int, help="Stop after N cases")
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Skip cases that need a model call (keeps routing and scope checks)",
    )
    parser.add_argument(
        "--real-model-only",
        action="store_true",
        help="Only the cases whose assertions need a real model to be meaningful",
    )
    parser.add_argument("--label", default="run", help="Label recorded in the report filename")
    args = parser.parse_args()

    cases = load_cases()
    if args.real_model_only:
        cases = [c for c in cases if c.get("requires_real_model")]
    if args.agent:
        wanted = args.agent if "." in args.agent else f"{PRIMARY_DOMAIN}.{args.agent}"
        cases = [c for c in cases if c.get("agent") == wanted or c.get("route_to") == wanted]
    if args.category:
        cases = [c for c in cases if c["category"] == args.category]
    if args.id:
        cases = [c for c in cases if c["id"] == args.id]
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        print("No cases matched the filters.")
        return 1

    config = run_configuration()
    print(f"provider: {config['llm_provider']} ({config['llm_model']})")
    print(f"cases   : {len(cases)}")
    if args.no_generate:
        print("mode    : no-generate (routing and scope only)")
    print()

    results: list[CaseResult] = []
    started = time.perf_counter()

    with TestClient(app) as client:
        email = f"eval+{uuid.uuid4().hex[:8]}@example.com"
        token = client.post(
            "/api/auth/register",
            json={"name": "Eval Runner", "email": email, "password": "EvalPass123"},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        client.put(
            f"/api/profile/domain/{PRIMARY_DOMAIN}",
            headers=headers,
            json={"profile_data": BRAND},
        )
        for key, data in AGENT_PROFILES.items():
            client.put(
                f"/api/profile/agent/{key}", headers=headers, json={"profile_data": data}
            )
        for memory in SEED_MEMORIES:
            client.post("/api/memory", headers=headers, json=memory)

        for index, case in enumerate(cases, start=1):
            agent = case.get("agent", "")
            result = CaseResult(
                case_id=case["id"],
                agent=agent,
                category=case["category"],
                request=case["request"].strip(),
                rubric=list(case.get("rubric", [])),
            )
            prefix = f"[{index}/{len(cases)}] {case['id']:34s}"

            try:
                if case["category"] == "routing":
                    assert_routing(result, case)
                elif case.get("expect_in_scope") is False:
                    # Handoffs cost no model call, so they always run.
                    response = client.post(
                        "/api/chat",
                        headers=headers,
                        json={"message": case["request"], "agent_key": agent},
                    )
                    if response.status_code != 200:
                        result.error = f"HTTP {response.status_code}"
                    else:
                        assert_handoff(result, case, response.json())
                elif args.no_generate:
                    result.skipped = "needs a model call"
                elif case.get("requires_real_model") and settings.LLM_PROVIDER == "mock":
                    # These cases assert that the MODEL followed an instruction.
                    # The local-dev composer ignores agent instructions by
                    # construction, so running them here would report a failure
                    # that says nothing about prompt quality.
                    result.skipped = "needs a real model"
                else:
                    payload: dict[str, Any] = {
                        "message": case["request"],
                        "agent_key": agent,
                    }
                    if "attachment_text" in case:
                        payload["attachment_name"] = case.get("attachment_name", "attachment.md")
                        payload["attachment_text"] = case["attachment_text"]
                    response = client.post("/api/chat", headers=headers, json=payload)
                    if response.status_code != 200:
                        result.error = f"HTTP {response.status_code}: {response.text[:120]}"
                    else:
                        assert_case(result, case, response.json())
            except Exception as exc:  # noqa: BLE001 - one bad case must not stop the run
                result.error = f"{type(exc).__name__}: {exc}"

            if result.skipped:
                print(f"{prefix} skipped")
            elif result.error:
                print(f"{prefix} \033[91mERROR\033[0m {result.error}")
            else:
                mark = "\033[92mok\033[0m" if not result.failures else "\033[91mFAIL\033[0m"
                print(
                    f"{prefix} {mark} {result.passed}/{len(result.assertions)}"
                    f"  {result.latency_ms:>6}ms"
                )
                for a, _p, d in result.failures:
                    print(f"      - {a}" + (f" → {d}" if d else ""))
            results.append(result)

    elapsed = time.perf_counter() - started
    json_path, md_path = write_reports(results, config, args.label, elapsed)

    total = sum(len(r.assertions) for r in results)
    failed = sum(len(r.failures) for r in results)
    errors = sum(1 for r in results if r.error)
    degraded = sum(
        1
        for r in results
        if any("came from the model" in a and not p for a, p, _ in r.assertions)
    )

    print("\n" + "=" * 70)
    print(f"cases              : {len(results)}")
    print(f"assertions         : {total - failed}/{total} passed")
    print(f"errors             : {errors}")
    print(f"degraded img specs : {degraded}")
    print(f"elapsed            : {elapsed:.0f}s")
    print(f"report (json)      : {json_path.relative_to(BACKEND)}")
    print(f"report (markdown)  : {md_path.relative_to(BACKEND)}")
    print("=" * 70)
    return 1 if (failed or errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
