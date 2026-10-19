#!/usr/bin/env python
"""Checks the judge's logic without calling a model.

Judging costs money and takes minutes, so everything that does not need a real
model is verified here first: reply parsing, score validation, repeat
aggregation, self-evaluation detection, the visual-dimension skip, and the two
output files. The fake provider returns exactly what real judges return,
including the fenced and chatty replies that break naive parsing.

    python scripts/check_judge.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from app.llm.base import LLMProviderError  # noqa: E402
from scripts.marketing_eval import judge as J  # noqa: E402
from scripts.marketing_eval.rubric import load_rubric  # noqa: E402

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content
        self.input_tokens = 100
        self.output_tokens = 20
        self.model = "fake"
        self.provider = "fake"


class FakeProvider:
    """Replies with whatever the script queues up."""

    name = "fake"
    default_model = "fake-judge"

    def __init__(self, replies: list[Any] | None = None, score: int = 4) -> None:
        self.replies = list(replies or [])
        self.score = score
        self.prompts: list[str] = []
        self.systems: list[str] = []
        self.kwargs: list[dict[str, Any]] = []

    def generate(self, messages, **kwargs):  # noqa: ANN001, ANN003
        self.prompts.append(messages[-1].content)
        self.systems.append(kwargs.get("system") or "")
        self.kwargs.append(kwargs)
        if self.replies:
            reply = self.replies.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return FakeResponse(reply)
        # Default: score every dimension the prompt asked for.
        asked = json.loads(
            messages[-1].content.split("exactly these keys and nothing else:")[1].strip()
        )
        return FakeResponse(
            json.dumps({name: {"score": self.score, "why": "fine"} for name in asked})
        )


def install(provider: FakeProvider) -> None:
    J.get_llm_provider = lambda: provider  # type: ignore[assignment]


def main() -> int:
    rubric = load_rubric()
    brand, profiles, brand_source = J.brand_context()

    print("1. the judge reads the reply formats real models actually send")
    good = '{"hook": {"score": 4, "why": "strong first line"}}'
    for label, raw in {
        "bare JSON": good,
        "fenced JSON": f"```json\n{good}\n```",
        "unlabelled fence": f"```\n{good}\n```",
        "JSON with prose around it": f"Here are my scores:\n{good}\nHope that helps.",
    }.items():
        try:
            parsed = J.extract_json(raw)
            check(label, parsed["hook"]["score"] == 4, str(parsed))
        except ValueError as exc:
            check(label, False, str(exc))
    for label, raw in {"prose only": "I think it was good.", "a JSON list": "[1, 2]"}.items():
        try:
            J.extract_json(raw)
        except ValueError:
            check(f"rejects {label}", True)
        else:
            check(f"rejects {label}", False, "parsed without complaint")

    print("\n2. only a usable 1-5 score is accepted")
    check(
        "a valid score passes",
        J.coerce_scores({"hook": {"score": 4, "why": "x"}}, ["hook"])["hook"]["score"] == 4,
    )
    check(
        "a bare number is tolerated",
        J.coerce_scores({"hook": 5}, ["hook"])["hook"]["score"] == 5,
    )
    check(
        "a string number is tolerated",
        J.coerce_scores({"hook": {"score": "3"}}, ["hook"])["hook"]["score"] == 3,
    )
    check(
        "a float is rounded",
        J.coerce_scores({"hook": {"score": 3.6}}, ["hook"])["hook"]["score"] == 4,
    )
    for label, payload in {
        "a score of 0": {"hook": {"score": 0}},
        "a score of 9": {"hook": {"score": 9}},
        "a missing dimension": {"other": {"score": 4}},
        "a non-numeric score": {"hook": {"score": "great"}},
        "a null score": {"hook": {"score": None}},
    }.items():
        try:
            J.coerce_scores(payload, ["hook"])
        except ValueError:
            check(f"rejects {label}", True)
        else:
            check(f"rejects {label}", False, "accepted")
    check(
        "an extra dimension the judge invented is dropped",
        set(J.coerce_scores({"hook": {"score": 4}, "made_up": {"score": 5}}, ["hook"]))
        == {"hook"},
    )

    print("\n3. the prompt carries the brand, the request, the output and the anchors")
    report_path = J.resolve_report("CLOUD-gemma4-fixed")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    check("resolve_report() found the run by label", report_path.exists(), report_path.name)
    copy_case = next(c for c in report["cases"] if c["id"] == "copy-ordinary-linkedin")
    prompt = J.build_prompt(copy_case, copy_case["rubric"], rubric, brand, profiles)
    check("the brand name is in the prompt", "Acme Cloud" in prompt)
    check("the banned terms are in the prompt", "clickbait" in prompt and "emojis" in prompt)
    check("the agent's own profile is in the prompt", "LinkedIn" in prompt)
    check("the request is in the prompt", copy_case["request"][:40] in prompt)
    check("the output is in the prompt", copy_case["output"][:40] in prompt)
    check(
        "every declared dimension appears with its anchors",
        all(f"- {name}:" in prompt for name in copy_case["rubric"]),
    )
    check(
        "an anchor's wording is passed through verbatim",
        rubric.get("hook").anchors[5] in prompt,
    )
    check("the five-point scale is in the prompt", all(f"{n} = " in prompt for n in range(1, 6)))
    # v1 of the prompt produced only 1s, 3s and 5s across 174 scores, because
    # the dimension tables anchor those three levels and the judge read them as
    # the only legal answers. These two assertions guard the fix.
    check(
        "the prompt tells the judge to use 2 and 4",
        "2 and 4" in prompt,
    )
    check(
        "the system prompt explains what 2 and 4 mean",
        "2 and 4" in J.SYSTEM_PROMPT and "short of the" in J.SYSTEM_PROMPT,
    )
    check(
        "the system prompt reserves 5 for publishable work",
        "no edit at all" in J.SYSTEM_PROMPT,
    )
    check(
        "the judge is told an explicit request beats a standing default",
        "overrides the standing" in J.SYSTEM_PROMPT,
    )

    print("\n4. an image case shows the spec and alt text, and skips the visual dimensions")
    image_case = next(c for c in report["cases"] if c["id"] == "image-ordinary-linkedin")
    described = J.describe_output(image_case)
    check("the alt text is shown", image_case["media"][0]["alt_text"][:30] in described)
    check("the headline spec is shown", "headline" in described)
    check("the pixel size is shown", "1200x627" in described)
    check(
        "the judge is told it cannot see the pixels",
        "not the pixels" in described,
    )
    provider = FakeProvider()
    install(provider)
    usage = J.Usage()
    result = J.score_case(
        image_case, rubric, brand, profiles, model="fake-judge", usage=usage, repeat=1
    )
    check(
        "legibility and brand_fit are reported unjudged",
        set(result["unjudged"]) == {"legibility", "brand_fit"},
        ", ".join(sorted(result["unjudged"])),
    )
    check(
        "the remaining dimensions were scored",
        set(result["dimensions"]) == {"headline_relevance", "headline_brevity", "alt_text"},
        ", ".join(result["dimensions"]),
    )
    check(
        "a skipped dimension was never sent to the judge",
        "- legibility:" not in provider.prompts[0],
    )
    check("the judge ran at temperature 0", provider.kwargs[0]["temperature"] == 0.0)
    check("the judge model was passed through", provider.kwargs[0]["model"] == "fake-judge")
    check("the editor system prompt was used", "senior marketing editor" in provider.systems[0])

    print("\n5. a malformed reply is retried, then recorded as a failure")
    provider = FakeProvider(replies=["not json at all", '{"hook": {"score": 5}}'])
    install(provider)
    usage = J.Usage()
    case = {"id": "retry-case", "agent": "marketing.social-copy", "category": "ordinary",
            "request": "r", "output": "o", "rubric": ["hook"], "media": []}
    result = J.score_case(case, rubric, brand, profiles, model="m", usage=usage, repeat=1)
    check("the retry recovered a score", result["dimensions"].get("hook", {}).get("score") == 5)
    check("the retry was counted", usage.retries == 1, str(usage.retries))
    check("the retry prompt said the reply was invalid", "not valid JSON" in provider.prompts[1])

    provider = FakeProvider(replies=["nope", "still nope"])
    install(provider)
    usage = J.Usage()
    result = J.score_case(case, rubric, brand, profiles, model="m", usage=usage, repeat=1)
    check("two bad replies leave the case unscored", result["dimensions"] == {})
    check("the failure is recorded on the case", bool(result["error"]), str(result["error"]))
    check("the failure is recorded in usage", len(usage.failures) == 1)

    provider = FakeProvider(replies=[LLMProviderError("connection refused")])
    install(provider)
    usage = J.Usage()
    result = J.score_case(case, rubric, brand, profiles, model="m", usage=usage, repeat=1)
    check("a provider error does not crash the run", result["dimensions"] == {})
    check(
        "the provider error is reported",
        any("connection refused" in f for f in usage.failures),
        "; ".join(usage.failures),
    )

    print("\n6. repeats produce a median and an honest spread")
    replies = [
        '{"hook": {"score": 3, "why": "a"}}',
        '{"hook": {"score": 5, "why": "b"}}',
        '{"hook": {"score": 4, "why": "c"}}',
    ]
    provider = FakeProvider(replies=replies)
    install(provider)
    usage = J.Usage()
    result = J.score_case(case, rubric, brand, profiles, model="m", usage=usage, repeat=3)
    entry = result["dimensions"]["hook"]
    check("three runs were recorded", len(result["runs"]) == 3)
    check("the score is the median", entry["score"] == 4, str(entry["score"]))
    check("the spread is max-min", entry["spread"] == 2, str(entry["spread"]))
    check("disagreement is not called unanimous", entry["unanimous"] is False)
    check("the individual runs are kept", entry["runs"] == [3, 5, 4], str(entry["runs"]))

    provider = FakeProvider(replies=['{"hook": {"score": 4}}'] * 3)
    install(provider)
    result = J.score_case(case, rubric, brand, profiles, model="m", usage=J.Usage(), repeat=3)
    entry = result["dimensions"]["hook"]
    check("identical runs are unanimous", entry["unanimous"] is True)
    check("identical runs have zero spread", entry["spread"] == 0)

    result_once = J.score_case(
        case, rubric, brand, profiles, model="m",
        usage=J.Usage(), repeat=1,
    )
    check(
        "a single run claims no spread at all",
        "spread" not in result_once["dimensions"]["hook"],
        "unknown is not the same as zero",
    )

    print("\n7. the summary aggregates what it was given")
    provider = FakeProvider(score=4)
    install(provider)
    usage = J.Usage()
    scored = [
        J.score_case(c, rubric, brand, profiles, model="m", usage=usage, repeat=1)
        for c in report["cases"]
        if c.get("rubric")
    ]
    summary = J.summarise(scored, rubric)
    check("the mean is right", summary["mean"] == 4.0, str(summary["mean"]))
    check(
        "every scored dimension is counted once",
        summary["scored_dimensions"] == sum(len(c["dimensions"]) for c in scored),
        str(summary["scored_dimensions"]),
    )
    check(
        "the distribution sums to the number of scores",
        sum(summary["distribution"].values()) == summary["scored_dimensions"],
    )
    check(
        "unjudged dimensions are counted, not scored",
        summary["unjudged_dimensions"] == sum(len(c["unjudged"]) for c in scored)
        and summary["unjudged_dimensions"] > 0,
        str(summary["unjudged_dimensions"]),
    )
    check(
        "every agent in the report appears",
        len(summary["by_agent"]) == len({c["agent"] for c in scored if c["agent"]}),
        ", ".join(summary["by_agent"]),
    )
    check(
        "groups come from the rubric",
        set(summary["by_group"]) <= set(rubric.groups()),
        ", ".join(summary["by_group"]),
    )
    check("no case failed with a well-behaved judge", summary["failed_cases"] == [])
    check(
        "a single-run summary claims no reliability figure",
        "reliability" not in summary,
    )

    print("\n8. cost is reported only when the rate is known")
    usage = J.Usage()
    usage.input_tokens, usage.output_tokens = 1_000_000, 1_000_000
    check(
        "a known model is priced from the published rate",
        usage.cost_usd("gemma4:31b") == 0.54,
        str(usage.cost_usd("gemma4:31b")),
    )
    check("an unknown model reports no cost", usage.cost_usd("mystery-model:1t") is None)
    check("zero tokens reports no cost", J.Usage().cost_usd("gemma4:31b") is None)

    print("\n9. self-evaluation is detected and stated, not buried")
    payload_self = {
        "report": {"file": "r.json", "label": "L", "generated_at": "now",
                   "llm_model": "gemma4:31b", "llm_provider": "openai",
                   "llm_temperature": 0.4},
        "judge": {"model": "gemma4:31b", "provider": "openai", "temperature": 0.0,
                  "repeat": 1, "prompt_version": J.PROMPT_VERSION,
                  "self_evaluation": True, "rubric_file": rubric.source.name,
                  "rubric_dimensions": len(rubric), "brand_source": brand_source,
                  "calls": 21, "retries": 0, "input_tokens": 1000,
                  "output_tokens": 200, "cost_usd": 0.0002,
                  "elapsed_seconds": 12.0, "failures": []},
        "summary": summary,
        "cases": scored,
    }
    out = Path("/tmp/_judge_selfeval.scores.md")
    J.write_markdown(out, payload_self, rubric)
    text = out.read_text(encoding="utf-8")
    check("the warning is in the markdown", "WARNING — self-evaluation" in text)
    check("it names the model responsible", "gemma4:31b" in text)
    check("it says what to do instead", "--model" in text)
    check("the judge model is recorded", "Judged by: **gemma4:31b**" in text)
    check("the generating model is recorded", "Generated by: **gemma4:31b**" in text)
    check("the prompt version is recorded", f"prompt v{J.PROMPT_VERSION}" in text)
    check("the rubric file is recorded", rubric.source.name in text)
    check("the biases are stated", "favours its own output" in text)
    check("per-dimension means are tabulated", "## By dimension" in text)
    check("per-agent means are tabulated", "## By agent" in text)
    check("unjudged dimensions are explained", "not scored" in text)
    check("the cost is stated", "$0.0002" in text)

    payload_other = json.loads(json.dumps(payload_self))
    payload_other["judge"]["model"] = "deepseek-v4-pro"
    payload_other["judge"]["self_evaluation"] = False
    payload_other["judge"]["cost_usd"] = None
    out2 = Path("/tmp/_judge_other.scores.md")
    J.write_markdown(out2, payload_other, rubric)
    text2 = out2.read_text(encoding="utf-8")
    check("a different judge gets no warning", "WARNING — self-evaluation" not in text2)
    check(
        "an unpriced model claims no cost",
        "no cost is claimed" in text2 and "$" not in text2.split("## By agent")[0].split(
            "Judging used"
        )[1],
    )
    out.unlink(missing_ok=True)
    out2.unlink(missing_ok=True)

    print(f"\n{len(scored)} cases exercised against a fake judge, no model calls made")
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL JUDGE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
