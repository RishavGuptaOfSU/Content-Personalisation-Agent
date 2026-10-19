#!/usr/bin/env python
"""Scores the qualitative dimensions of an eval report with an LLM judge.

The harness decides everything a machine can decide deterministically. This
covers the part it deliberately leaves alone: whether the output is any *good*.
It reads a report the harness already wrote — no agents are re-run, so the
numbers describe exactly the outputs in that file.

    python scripts/marketing_eval/judge.py CLOUD-gemma4-fixed
    python scripts/marketing_eval/judge.py <report>.json --model deepseek-v4-pro
    python scripts/marketing_eval/judge.py CLOUD-gemma4-fixed --repeat 3

Writes ``<report>.scores.json`` and ``<report>.scores.md`` next to the report.

What these scores are not
-------------------------
An LLM judge is a cheap proxy for a human reader, not a replacement. Three
biases are worth naming, because a number on a page hides them:

* **Self-preference.** A model scores its own output higher. When the judge and
  the generator are the same model this script says so, loudly, everywhere.
* **Verbosity.** Judges tend to reward longer answers. Reply length is in the
  report, so check whether score tracks length before believing a win.
* **Position and leniency.** Scores cluster at 4. A 0.2 difference between two
  runs is noise; use ``--repeat`` to see the spread before calling it a change.

Scores are comparable between runs only when the judge model, the rubric and
the prompt are identical. All three are recorded in the output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from app.core.config import settings  # noqa: E402
from app.llm.base import ChatMessage, LLMProviderError  # noqa: E402
from app.llm.registry import get_llm_provider  # noqa: E402
from scripts.marketing_eval.rubric import Rubric, load_rubric  # noqa: E402

REPORT_DIR = HERE / "reports"

#: Every model the Ollama Cloud free plan served on 2026-10-19, measured by
#: sending all 22 entries in /api/tags a 5-token request. Seven answered 200.
#: The other fifteen answered HTTP 402 "not included in your free usage"
#: (deepseek-v4-pro, deepseek-v4.1-flash, glm-5.2, glm-5.3, glm-5.3-flash,
#: kimi-k2.6, kimi-k3, kimi-k2.7-code, minimax-m2.7, minimax-m3,
#: mistral-large-3, muse-spark-open), HTTP 403 "being rolled out"
#: (mistral-large-4), or HTTP 400 because they are not chat models at all
#: (clef:27b is a decision model and only serves /v1/systemone).
#: Re-probe before trusting this: plans change.
FREE_PLAN_MODELS = (
    "gemma4:31b",
    "gpt-oss:120b",
    "gpt-oss:20b",
    "nemotron-3-nano:30b",
    "nemotron-3-super",
    "nemotron-3-ultra",
    "beam",
)

#: The free models that spend completion tokens on hidden reasoning before
#: answering. Measured: a 17-word sentence cost nemotron-3-super 84 completion
#: tokens and beam 106, against 20-30 for a non-reasoning model. They are not
#: worse for it, but they are competing for the same ``LLM_MAX_TOKENS`` budget,
#: so a tight budget truncates their visible answer rather than their thinking.
REASONING_MODELS = (
    "nemotron-3-nano:30b",
    "nemotron-3-super",
    "nemotron-3-ultra",
    "beam",
)

#: Published Ollama Cloud rates, USD per million tokens, as of 2026-10.
#: Only used to report cost for models we have a rate for; an unknown model
#: reports tokens and no cost rather than a guess.
PRICING_USD_PER_MTOK: dict[str, tuple[float, float]] = {
    "gemma4:31b": (0.14, 0.40),
    "glm-5.3-flash": (0.15, 0.50),
    "glm-5.3": (1.40, 4.40),
    "deepseek-v4.1-flash": (0.30, 1.20),
    "deepseek-v4-pro:0813": (1.32, 3.96),
    "deepseek-v4-pro": (1.32, 3.96),
}

#: Bumped whenever the prompt below changes, because scores produced by two
#: different prompts are not comparable and nothing else would reveal that.
#: v1 produced only 1s, 3s and 5s across 174 scores — the dimension tables give
#: anchors for those three levels, and the judge treated them as the only legal
#: answers. v2 names 2 and 4 explicitly and says an explicit request beats a
#: standing default.
PROMPT_VERSION = "2"

SYSTEM_PROMPT = """\
You are a senior marketing editor reviewing a junior's work. You are fair but \
hard to impress: you score what is on the page, not what it was trying to do.

You will be given the brand context, the request that was made, the output that \
was produced, and a scoring rubric. Score only the dimensions you are asked \
about, using the anchors given for each.

Rules:
- The rubric describes levels 1, 3 and 5. Use 2 and 4 as well: 2 means better \
than the 1 anchor but short of the 3, and 4 means better than the 3 anchor but \
short of the 5. Most competent work lands on 4, not 5. Do not restrict yourself \
to 1, 3 and 5.
- Reserve 5 for output you would publish with no edit at all. If you can name \
an edit you would make, the score is at most 4.
- Score the output as delivered. Do not reward intent or potential.
- An explicit instruction in the request overrides the standing brand or agent \
configuration. Honouring the request over a conflicting default is correct, not \
a failure.
- Judge against the brand context, not your own taste.
- Length is not quality. A short output that does the job scores higher than a \
long one that pads.
- Give a reason of at most 25 words, naming the specific thing in the output \
that decided the score.
- Reply with JSON only. No prose, no code fence, no commentary.
"""


# ------------------------------------------------------------------- loading
def resolve_report(target: str) -> Path:
    """Accept a path, a filename, or a run label."""
    direct = Path(target)
    if direct.is_file():
        return direct
    candidate = REPORT_DIR / target
    if candidate.is_file():
        return candidate
    # ``.scores`` files are this script's own output, including archived copies
    # like ``.scores-promptv1.json``; they are never a judgeable report.
    reports = [path for path in REPORT_DIR.glob("*.json") if ".scores" not in path.name]
    matches = sorted(
        path
        for path in reports
        if target in path.stem or target == json.loads(path.read_text()).get("label")
    )
    if not matches:
        available = ", ".join(sorted(path.stem for path in reports))
        raise SystemExit(f"No report matching {target!r}.\nAvailable: {available}")
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise SystemExit(f"{target!r} matches several reports: {names}")
    return matches[-1]


def brand_context() -> tuple[dict[str, Any], dict[str, dict[str, Any]], str]:
    """The brand and per-agent profiles the harness actually configured.

    Imported from the harness rather than restated here, so the judge can never
    score against a brand the run did not use.
    """
    from scripts.marketing_eval.harness import AGENT_PROFILES, BRAND

    return BRAND, AGENT_PROFILES, "scripts/marketing_eval/harness.py"


# -------------------------------------------------------------------- prompt
def describe_output(case: dict[str, Any]) -> str:
    """The output as a text judge can actually see it."""
    parts = [case.get("output") or "(empty output)"]
    for item in case.get("media") or []:
        spec = item.get("spec") or {}
        lines = [
            "",
            "--- rendered image (the judge sees this description, not the pixels) ---",
            f"size: {item.get('width')}x{item.get('height')}",
            f"alt text: {item.get('alt_text') or '(none)'}",
        ]
        if spec:
            lines.append("spec: " + json.dumps(spec, ensure_ascii=False))
        parts.append("\n".join(lines))
    return "\n".join(parts)


def build_prompt(
    case: dict[str, Any],
    dimensions: list[str],
    rubric: Rubric,
    brand: dict[str, Any],
    agent_profiles: dict[str, dict[str, Any]],
) -> str:
    profile = agent_profiles.get(case.get("agent") or "", {})
    dims = rubric.subset(dimensions)
    blocks = [
        "=== BRAND CONTEXT ===",
        json.dumps(brand, indent=2, ensure_ascii=False),
        "",
        f"This agent was also configured with: {json.dumps(profile, ensure_ascii=False)}"
        if profile
        else "This agent had no extra configuration.",
        "",
        "=== THE REQUEST ===",
        (case.get("request") or "").strip(),
        "",
        "=== THE OUTPUT ===",
        describe_output(case),
        "",
        "=== SCALE ===",
        "Score 1-5. Use every value, including 2 and 4.",
        rubric.scale_block(),
        "",
        "=== DIMENSIONS TO SCORE ===",
        "Each dimension gives you the 1, 3 and 5 anchors. When the output sits "
        "between two anchors, use the even number between them.",
        "\n".join(dim.prompt_block() for dim in dims),
        "",
        "=== REPLY FORMAT ===",
        "JSON object, exactly these keys and nothing else:",
        json.dumps(
            {name: {"score": 3, "why": "short reason"} for name in dimensions},
            indent=2,
        ),
    ]
    return "\n".join(blocks)


# --------------------------------------------------------------------- parse
_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.MULTILINE)


def extract_json(text: str) -> dict[str, Any]:
    """Pull the JSON object out of a model reply.

    Judges wrap JSON in fences and prose despite instructions. This tolerates
    that but not malformed JSON: a reply we cannot read must surface as a
    failure, not as a silently missing score.
    """
    cleaned = _FENCE.sub("", text).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise ValueError(f"no JSON object in judge reply: {text[:160]!r}") from None
        parsed = json.loads(cleaned[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError(f"judge returned {type(parsed).__name__}, expected an object")
    return parsed


def coerce_scores(parsed: dict[str, Any], expected: list[str]) -> dict[str, dict[str, Any]]:
    """Validate the judge's object against the dimensions we asked for."""
    out: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for name in expected:
        entry = parsed.get(name)
        if isinstance(entry, int | float | str):  # tolerate a bare score
            entry = {"score": entry, "why": ""}
        if not isinstance(entry, dict) or "score" not in entry:
            missing.append(name)
            continue
        try:
            score = int(round(float(entry["score"])))
        except (TypeError, ValueError):
            missing.append(name)
            continue
        if not 1 <= score <= 5:
            missing.append(name)
            continue
        out[name] = {"score": score, "why": str(entry.get("why") or "").strip()}
    if missing:
        raise ValueError(f"judge did not return a usable 1-5 score for {missing}")
    return out


# --------------------------------------------------------------------- judge
@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    retries: int = 0
    failures: list[str] = field(default_factory=list)

    def add(self, response: Any) -> None:
        self.calls += 1
        self.input_tokens += int(response.input_tokens or 0)
        self.output_tokens += int(response.output_tokens or 0)

    def cost_usd(self, model: str) -> float | None:
        rate = PRICING_USD_PER_MTOK.get(model)
        if not rate or not (self.input_tokens or self.output_tokens):
            return None
        return (self.input_tokens * rate[0] + self.output_tokens * rate[1]) / 1_000_000


def score_case(
    case: dict[str, Any],
    rubric: Rubric,
    brand: dict[str, Any],
    agent_profiles: dict[str, dict[str, Any]],
    *,
    model: str | None,
    usage: Usage,
    repeat: int,
) -> dict[str, Any]:
    scorable, skipped = rubric.judgeable(case.get("rubric") or [])
    result: dict[str, Any] = {
        "id": case["id"],
        "agent": case.get("agent"),
        "category": case.get("category"),
        "output_chars": len(case.get("output") or ""),
        "latency_ms": case.get("latency_ms"),
        "unjudged": {
            name: "needs the rendered image; see rubric.md and probe_renderer.py"
            for name in skipped
        },
        "runs": [],
        "dimensions": {},
        "error": None,
    }
    if not scorable:
        return result

    prompt = build_prompt(case, scorable, rubric, brand, agent_profiles)
    provider = get_llm_provider()

    for attempt in range(repeat):
        reply = None
        for retry in range(2):
            try:
                response = provider.generate(
                    [ChatMessage(role="user", content=prompt if retry == 0 else prompt
                                 + "\n\nYour previous reply was not valid JSON. "
                                   "Reply with the JSON object only.")],
                    system=SYSTEM_PROMPT,
                    temperature=0.0,
                    max_tokens=900,
                    model=model,
                )
            except LLMProviderError as exc:
                usage.failures.append(f"{case['id']}: provider error: {exc}")
                break
            usage.add(response)
            try:
                reply = coerce_scores(extract_json(response.content), scorable)
                break
            except ValueError as exc:
                usage.retries += 1
                if retry == 1:
                    usage.failures.append(f"{case['id']}: {exc}")
        if reply is not None:
            result["runs"].append(reply)

    if not result["runs"]:
        result["error"] = "the judge produced no usable score for this case"
        return result

    # Aggregate the repeats: the median is the score, the spread is how much to
    # trust it. With repeat=1 the spread is unknown, not zero.
    for name in scorable:
        scores = [run[name]["score"] for run in result["runs"] if name in run]
        if not scores:
            continue
        entry: dict[str, Any] = {
            "score": statistics.median(scores),
            "why": next((run[name]["why"] for run in result["runs"] if name in run), ""),
            "runs": scores,
        }
        if len(scores) > 1:
            entry["spread"] = max(scores) - min(scores)
            entry["unanimous"] = len(set(scores)) == 1
        result["dimensions"][name] = entry
    return result


# ----------------------------------------------------------------- aggregate
def mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 2) if values else None


def summarise(scored: list[dict[str, Any]], rubric: Rubric) -> dict[str, Any]:
    all_scores: list[float] = []
    by_dimension: dict[str, list[float]] = {}
    by_agent: dict[str, list[float]] = {}
    by_group: dict[str, list[float]] = {}
    spreads: list[int] = []
    unanimous = 0
    repeated = 0

    for case in scored:
        for name, entry in case["dimensions"].items():
            score = float(entry["score"])
            all_scores.append(score)
            by_dimension.setdefault(name, []).append(score)
            by_agent.setdefault(case["agent"] or "(routed)", []).append(score)
            by_group.setdefault(rubric.get(name).group, []).append(score)
            if "spread" in entry:
                repeated += 1
                spreads.append(int(entry["spread"]))
                unanimous += bool(entry["unanimous"])

    summary: dict[str, Any] = {
        "scored_cases": sum(1 for case in scored if case["dimensions"]),
        "scored_dimensions": len(all_scores),
        "unjudged_dimensions": sum(len(case["unjudged"]) for case in scored),
        "failed_cases": [case["id"] for case in scored if case["error"]],
        "mean": mean(all_scores),
        "distribution": {
            str(level): sum(1 for score in all_scores if round(score) == level)
            for level in (1, 2, 3, 4, 5)
        },
        "by_dimension": {
            name: mean(scores) for name, scores in sorted(by_dimension.items())
        },
        "by_agent": {name: mean(scores) for name, scores in sorted(by_agent.items())},
        "by_group": {name: mean(scores) for name, scores in sorted(by_group.items())},
        "weakest_dimensions": [
            name
            for name, score in sorted(
                ((n, mean(s)) for n, s in by_dimension.items()), key=lambda kv: kv[1]
            )[:5]
        ],
    }
    if repeated:
        summary["reliability"] = {
            "dimensions_repeated": repeated,
            "mean_spread": mean([float(value) for value in spreads]),
            "max_spread": max(spreads),
            "unanimous_fraction": round(unanimous / repeated, 2),
            "note": "spread is max-min across repeats of an identical prompt at "
            "temperature 0; anything above 0 is judge noise, not a quality signal",
        }
    return summary


# ------------------------------------------------------------------- writing
def write_markdown(path: Path, payload: dict[str, Any], rubric: Rubric) -> None:
    meta = payload["judge"]
    summary = payload["summary"]
    lines = [
        f"# Qualitative scores — {payload['report']['label']}",
        "",
        f"Report: `{payload['report']['file']}` "
        f"({payload['report']['generated_at']})",
        f"Generated by: **{payload['report']['llm_model']}** "
        f"via {payload['report']['llm_provider']}",
        f"Judged by: **{meta['model']}** via {meta['provider']} "
        f"(temperature 0, prompt v{meta['prompt_version']}, "
        f"{meta['repeat']} run(s) per case)",
        f"Rubric: `{rubric.source.name}`, {len(rubric)} dimensions defined",
        "",
    ]
    if payload["report"].get("agent_models"):
        lines.insert(
            4,
            "Per-agent overrides in that run: "
            + ", ".join(
                f"`{agent}` → **{model}**"
                for agent, model in sorted(payload["report"]["agent_models"].items())
            ),
        )
    if meta["self_evaluation"]:
        lines += [
            "> **WARNING — self-evaluation.** The judge and the generator are the "
            f"same model (`{meta['model']}`). Models reliably score their own "
            "output higher, so treat these numbers as an upper bound, not a "
            "measurement. Re-run with `--model <a different model>` to get a "
            "comparable figure.",
            "",
        ]
    if summary["failed_cases"]:
        lines += [
            f"> **{len(summary['failed_cases'])} case(s) produced no score:** "
            + ", ".join(summary["failed_cases"]),
            "",
        ]

    lines += [
        "## Summary",
        "",
        f"- Mean score: **{summary['mean']} / 5** across "
        f"{summary['scored_dimensions']} dimension scores in "
        f"{summary['scored_cases']} cases",
        "- Score distribution (1→5): "
        + ", ".join(f"{k}:{v}" for k, v in summary["distribution"].items()),
        f"- Not judged by the model: {summary['unjudged_dimensions']} "
        "dimension(s) that need the rendered image",
    ]
    if "reliability" in summary:
        rel = summary["reliability"]
        lines.append(
            f"- Judge agreement across repeats: {rel['unanimous_fraction']:.0%} "
            f"identical, mean spread {rel['mean_spread']}, worst {rel['max_spread']}"
        )
    if meta["cost_usd"] is not None:
        lines.append(
            f"- Judging cost: ${meta['cost_usd']:.4f} "
            f"({meta['input_tokens']:,} in / {meta['output_tokens']:,} out tokens, "
            f"{meta['calls']} calls, {meta['elapsed_seconds']}s)"
        )
    else:
        lines.append(
            f"- Judging used {meta['input_tokens']:,} in / "
            f"{meta['output_tokens']:,} out tokens over {meta['calls']} calls "
            f"in {meta['elapsed_seconds']}s (no published rate for this model, "
            "so no cost is claimed)"
        )

    lines += ["", "## By agent", "", "| Agent | Mean |", "|---|---|"]
    lines += [f"| {name} | {score} |" for name, score in summary["by_agent"].items()]

    lines += ["", "## By dimension", "", "| Dimension | Group | Mean |", "|---|---|---|"]
    for name, score in sorted(summary["by_dimension"].items(), key=lambda kv: kv[1]):
        lines.append(f"| `{name}` | {rubric.get(name).group} | {score} |")

    lines += ["", "## Per case", ""]
    for case in payload["cases"]:
        header = f"### {case['id']}  —  {case['agent'] or '(routed)'}"
        lines += [header, ""]
        if case["error"]:
            lines += [f"*{case['error']}*", ""]
        if case["dimensions"]:
            lines += ["| Dimension | Score | Why |", "|---|---|---|"]
            for name, entry in case["dimensions"].items():
                why = entry["why"].replace("|", "/")
                spread = (
                    f" (runs: {entry['runs']})" if entry.get("spread", 0) else ""
                )
                lines.append(f"| `{name}` | {entry['score']}/5{spread} | {why} |")
            lines.append("")
        for name, reason in case["unjudged"].items():
            lines.append(f"- `{name}`: not scored — {reason}")
        if case["unjudged"]:
            lines.append("")

    lines += [
        "## How to read this",
        "",
        "These are an LLM's opinions against the anchors in "
        f"`{rubric.source.name}`, not measurements. Known biases: a judge "
        "favours its own output, favours longer answers, and clusters around 4. "
        "Compare two runs only when the judge model, rubric and prompt version "
        "all match — all three are recorded above. Treat differences smaller "
        "than the mean spread as noise.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("report", help="report path, filename or run label")
    parser.add_argument(
        "--model",
        default=os.environ.get("JUDGE_MODEL"),
        help="judge model (default: the configured provider model)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="score each case N times to measure judge self-consistency",
    )
    parser.add_argument("--only", action="append", help="limit to these case ids")
    parser.add_argument("--limit", type=int, help="score only the first N cases")
    args = parser.parse_args()

    if args.repeat < 1:
        raise SystemExit("--repeat must be at least 1")

    report_path = resolve_report(args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    rubric = load_rubric()
    brand, agent_profiles, brand_source = brand_context()

    provider = get_llm_provider()
    judge_model = args.model or provider.default_model
    generator_model = report.get("configuration", {}).get("llm_model")
    self_eval = bool(generator_model) and judge_model == generator_model

    candidates = [
        case
        for case in report["cases"]
        if case.get("rubric") and not case.get("skipped") and not case.get("error")
    ]
    if args.only:
        wanted = set(args.only)
        candidates = [case for case in candidates if case["id"] in wanted]
        unknown = wanted - {case["id"] for case in candidates}
        if unknown:
            raise SystemExit(f"No scorable case with id: {', '.join(sorted(unknown))}")
    if args.limit:
        candidates = candidates[: args.limit]
    if not candidates:
        raise SystemExit("Nothing to score in this report.")

    print(f"Report : {report_path.name}  (label {report.get('label')!r})")
    print(f"Output generated by: {generator_model} via "
          f"{report.get('configuration', {}).get('llm_provider')}")
    pinned = report.get("configuration", {}).get("agent_models") or {}
    if pinned:
        print("Per-agent overrides: "
              + ", ".join(f"{a}={m}" for a, m in sorted(pinned.items())))
    print(f"Judge  : {judge_model} via {provider.name}, temperature 0, "
          f"repeat {args.repeat}")
    print(f"Rubric : {rubric.source.name} "
          f"({len(rubric)} dimensions, {len(rubric.visual_only)} not text-judgeable)")
    print(f"Brand  : from {brand_source}")
    if self_eval:
        print()
        print("!! WARNING: the judge IS the model that produced these outputs.")
        print("!! Models score their own work high. Read this as an upper bound,")
        print("!! and re-run with --model <other model> for a usable number.")
    print(f"\nScoring {len(candidates)} case(s)...\n")

    usage = Usage()
    started = time.time()
    scored: list[dict[str, Any]] = []
    for index, case in enumerate(candidates, start=1):
        result = score_case(
            case,
            rubric,
            brand,
            agent_profiles,
            model=judge_model,
            usage=usage,
            repeat=args.repeat,
        )
        scored.append(result)
        if result["error"]:
            detail = result["error"]
        else:
            scores = [entry["score"] for entry in result["dimensions"].values()]
            detail = (
                f"mean {statistics.fmean(scores):.1f}  "
                + " ".join(
                    f"{name}={entry['score']}"
                    for name, entry in result["dimensions"].items()
                )
            )
        print(f"  [{index:2}/{len(candidates)}] {result['id']:<38} {detail}")

    elapsed = round(time.time() - started, 1)
    summary = summarise(scored, rubric)
    payload = {
        "report": {
            "file": report_path.name,
            "label": report.get("label"),
            "generated_at": report.get("generated_at"),
            "llm_model": generator_model,
            "llm_provider": report.get("configuration", {}).get("llm_provider"),
            "llm_temperature": report.get("configuration", {}).get("llm_temperature"),
            "agent_models": report.get("configuration", {}).get("agent_models") or {},
        },
        "judge": {
            "model": judge_model,
            "provider": provider.name,
            "temperature": 0.0,
            "repeat": args.repeat,
            "prompt_version": PROMPT_VERSION,
            "self_evaluation": self_eval,
            "rubric_file": rubric.source.name,
            "rubric_dimensions": len(rubric),
            "brand_source": brand_source,
            "calls": usage.calls,
            "retries": usage.retries,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cost_usd": usage.cost_usd(judge_model),
            "elapsed_seconds": elapsed,
            "failures": usage.failures,
        },
        "summary": summary,
        "cases": scored,
    }

    # Refuse to write an empty result over a previous good one. A total failure
    # is usually a bad model name or an expired key, and silently replacing real
    # scores with zeros would destroy the only copy of them.
    if not summary["scored_dimensions"]:
        print("\nThe judge scored nothing at all, so no files were written.")
        for failure in usage.failures[:5]:
            print(f"  - {failure}")
        if not usage.failures:
            print("  (no provider errors either — check --only/--limit filters)")
        return 1

    stem = report_path.with_suffix("")
    json_path = Path(f"{stem}.scores.json")
    md_path = Path(f"{stem}.scores.md")
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(md_path, payload, rubric)

    print(f"\nMean {summary['mean']}/5 over {summary['scored_dimensions']} "
          f"dimension scores in {summary['scored_cases']} cases")
    if summary["unjudged_dimensions"]:
        print(f"{summary['unjudged_dimensions']} dimension(s) left unjudged "
              "(need the rendered image)")
    if "reliability" in summary:
        rel = summary["reliability"]
        print(f"Judge agreement: {rel['unanimous_fraction']:.0%} identical across "
              f"repeats, mean spread {rel['mean_spread']}")
    if usage.failures:
        print(f"\n{len(usage.failures)} judge failure(s):")
        for failure in usage.failures[:10]:
            print(f"  - {failure}")
    cost = usage.cost_usd(judge_model)
    print(
        f"Judging: {usage.calls} calls, {usage.input_tokens:,} in / "
        f"{usage.output_tokens:,} out tokens, {elapsed}s"
        + (f", ${cost:.4f}" if cost is not None else ", cost unknown for this model")
    )
    print(f"\nWrote {json_path.name}\n      {md_path.name}")
    if self_eval:
        print("\nReminder: this was a self-evaluation. See the warning above.")
    return 1 if summary["failed_cases"] else 0


if __name__ == "__main__":
    if settings.LLM_PROVIDER == "mock":
        print(
            "LLM_PROVIDER=mock composes replies locally and cannot judge "
            "anything. Point at a real model first.",
            file=sys.stderr,
        )
    raise SystemExit(main())
