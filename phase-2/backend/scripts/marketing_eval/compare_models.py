#!/usr/bin/env python
"""Compares several judged runs to pick the best model per agent.

Reads every ``*.scores.json`` matching a label prefix and tabulates the judge's
per-agent and per-dimension means side by side, so a per-agent model choice is
made from evidence instead of from a model's reputation.

    python scripts/marketing_eval/compare_models.py BAKEOFF2
    python scripts/marketing_eval/compare_models.py BAKEOFF2 --noise 0.33

Refusals, not warnings
----------------------
It will not compare runs that are not comparable, because a table that silently
mixes them is worse than no table:

* a different judge model, judge prompt version or rubric file
* a different number of scored cases (a run with errors scored fewer cases, so
  its mean describes an easier subset)

What it will not do is pick for you where the gap is inside the noise. The judge
disagrees with itself by a known amount; a gap smaller than that is not a
result. ``--noise`` sets that floor (default: the measured 0.33).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

REPORT_DIR = HERE / "reports"

#: Total run-to-run variance, measured rather than assumed, and the single most
#: important number in this file: it is the size below which a difference is
#: not a result.
#:
#: Two sources stack. The judge disagrees with itself by a mean spread of
#: 0.51-0.54 across three repeats of an identical prompt at temperature 0. The
#: agents themselves generate at temperature 0.4, so a re-run produces different
#: output to score. Measured together: re-running the *same* model and judging
#: it again moved per-agent means by up to 0.37 (post-image, gemma4:31b, two
#: repeat-3 runs), with no configuration change at all.
#:
#: An earlier screening pass used 0.33 and duly "found" two per-agent winners.
#: Confirming them at repeat 3 showed one was 0.23 *worse* and the other 0.07
#: better. That is what this number exists to prevent.
DEFAULT_NOISE = 0.5


def load_runs(prefix: str) -> list[dict[str, Any]]:
    runs = []
    for path in sorted(REPORT_DIR.glob("*.scores.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        label = payload["report"].get("label") or ""
        if prefix.lower() not in label.lower():
            continue
        payload["_file"] = path.name
        runs.append(payload)
    if not runs:
        raise SystemExit(f"No judged runs matching {prefix!r} in {REPORT_DIR}")
    return runs


def assert_comparable(runs: list[dict[str, Any]]) -> tuple[str, int]:
    """Every run must share a judge, a prompt version, a rubric and a case set."""
    judges = {run["judge"]["model"] for run in runs}
    if len(judges) > 1:
        raise SystemExit(
            "These runs were judged by different models "
            f"({', '.join(sorted(judges))}), so their scores are not comparable."
        )
    versions = {run["judge"]["prompt_version"] for run in runs}
    if len(versions) > 1:
        raise SystemExit(
            f"Mixed judge prompt versions ({', '.join(sorted(versions))}). "
            "Re-judge every run with the current prompt before comparing."
        )
    rubrics = {run["judge"]["rubric_file"] for run in runs}
    if len(rubrics) > 1:
        raise SystemExit(f"Mixed rubric files ({', '.join(sorted(rubrics))}).")
    repeats = {run["judge"]["repeat"] for run in runs}
    if len(repeats) > 1:
        detail = ", ".join(
            f"{model_of(run)}={run['judge']['repeat']}" for run in runs
        )
        raise SystemExit(
            f"Mixed judge repeat counts ({detail}). A median of three runs and a "
            "single run do not carry the same uncertainty, so comparing them "
            "would read judge noise as a quality difference. Re-judge them all "
            "with the same --repeat."
        )
    return judges.pop(), len(runs)


def partition(runs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split into runs that scored the full case set, and ones that did not."""
    counts = [run["summary"]["scored_dimensions"] for run in runs]
    full = max(counts)
    return (
        [run for run in runs if run["summary"]["scored_dimensions"] == full],
        [run for run in runs if run["summary"]["scored_dimensions"] != full],
    )


def model_of(run: dict[str, Any]) -> str:
    return run["report"].get("llm_model") or "(unknown)"


def name_runs(runs: list[dict[str, Any]]) -> None:
    """Give every run a unique display name, in place as ``_name``.

    Two runs can share a base model and still be different configurations — a
    single-model run and a mixed fleet built on the same default, for instance.
    Keying a comparison table by model alone silently collapses them into one
    column, which is how you end up comparing a run against itself.
    """
    for run in runs:
        name = model_of(run)
        pins = run["report"].get("agent_models") or {}
        if pins:
            name += f"+{len(pins)}pin"
        run["_name"] = name

    counts: dict[str, int] = {}
    for run in runs:
        counts[run["_name"]] = counts.get(run["_name"], 0) + 1
    seen: dict[str, int] = {}
    for run in runs:
        base = run["_name"]
        if counts[base] > 1:
            seen[base] = seen.get(base, 0) + 1
            label = run["report"].get("label") or f"run{seen[base]}"
            run["_name"] = f"{base}[{label}]"


def harness_facts(run: dict[str, Any]) -> dict[str, Any]:
    """Elapsed time and assertion tally from the run this was judged from.

    Quality is not the only axis. A model that scores the same but takes three
    times as long is not an equal choice, and the scores file does not carry
    that, so the underlying report is read for it.
    """
    path = REPORT_DIR / run["report"]["file"]
    if not path.is_file():
        return {}
    report = json.loads(path.read_text(encoding="utf-8"))
    totals = report.get("totals", {})
    return {
        "elapsed": report.get("elapsed_seconds"),
        "passed": totals.get("passed"),
        "assertions": totals.get("assertions"),
        "errors": totals.get("errors"),
        "degraded": totals.get("degraded_image_specs"),
    }


def per_agent(run: dict[str, Any]) -> dict[str, float]:
    return {k: v for k, v in run["summary"]["by_agent"].items() if v is not None}


def per_dimension(run: dict[str, Any]) -> dict[str, float]:
    return {k: v for k, v in run["summary"]["by_dimension"].items() if v is not None}


def table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i])
        for i in range(len(headers))
    ]
    out = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip()]
    out.append("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        out.append("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))).rstrip())
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("prefix", help="label prefix shared by the runs, e.g. BAKEOFF2")
    parser.add_argument(
        "--noise",
        type=float,
        default=DEFAULT_NOISE,
        help=f"judge noise floor; gaps smaller than this are not a result (default {DEFAULT_NOISE})",
    )
    args = parser.parse_args()

    runs = load_runs(args.prefix)
    name_runs(runs)
    judge, count = assert_comparable(runs)
    comparable, excluded = partition(runs)

    print(f"Judged by : {judge} (prompt v{runs[0]['judge']['prompt_version']}, "
          f"rubric {runs[0]['judge']['rubric_file']})")
    print(f"Runs      : {count} matching {args.prefix!r}, "
          f"{len(comparable)} comparable")
    print(f"Noise floor: {args.noise} (judge disagreement with itself)")

    for run in excluded:
        print(
            f"\n!! EXCLUDED {run["_name"]}: scored "
            f"{run['summary']['scored_dimensions']} dimensions in "
            f"{run['summary']['scored_cases']} cases, not the full "
            f"{comparable[0]['summary']['scored_dimensions']} in "
            f"{comparable[0]['summary']['scored_cases']}. Cases that errored were "
            "never scored, so its mean describes an easier subset."
        )

    self_judged = [run for run in comparable if run["judge"]["self_evaluation"]]
    for run in self_judged:
        print(
            f"\n!! {run["_name"]} JUDGED ITSELF. Models score their own output "
            "higher, so treat its figures as an upper bound."
        )

    print("\n== Overall ==\n")
    rows = []
    ranked_runs = sorted(comparable, key=lambda r: -(r["summary"]["mean"] or 0))
    for run in ranked_runs:
        facts = harness_facts(run)
        flags = []
        if run["judge"]["self_evaluation"]:
            flags.append("self-judged")
        if facts.get("degraded"):
            flags.append(f"{facts['degraded']} degraded img spec")
        rows.append([
            run["_name"],
            f"{run['summary']['mean']}",
            f"{facts.get('passed', '?')}/{facts.get('assertions', '?')}",
            f"{facts.get('elapsed', '?')}s",
            str(run["summary"]["distribution"]),
            ", ".join(flags),
        ])
    print(table(
        ["model", "judged", "assertions", "elapsed", "distribution 1->5", "notes"], rows
    ))

    agents = sorted({agent for run in comparable for agent in per_agent(run)})
    models = [run["_name"] for run in comparable]
    scores = {run["_name"]: per_agent(run) for run in comparable}

    print("\n== Per agent ==\n")
    rows = []
    for agent in agents:
        values = {model: scores[model].get(agent) for model in models}
        best = max((v for v in values.values() if v is not None), default=None)
        row = [agent.replace("marketing.", "")]
        for model in models:
            value = values[model]
            if value is None:
                row.append("-")
            else:
                mark = "*" if best is not None and value >= best - 1e-9 else " "
                row.append(f"{value:.2f}{mark}")
        row.append(decision(values, args.noise))
        rows.append(row)
    print(table(["agent", *models, "best vs runner-up"], rows))
    print("\n* = best for that agent. The last column compares the top two only.")

    print("\n== Recommendation ==\n")
    # The top mean is not automatically the default. Any model within the noise
    # floor of the best is statistically tied with it, so the tie is broken on
    # something that *is* measured precisely: wall-clock time.
    top = ranked_runs[0]["summary"]["mean"] or 0
    tied = [run for run in ranked_runs if (run["summary"]["mean"] or 0) >= top - args.noise]
    if len(tied) > 1:
        names = ", ".join(
            f"{run["_name"]} {run['summary']['mean']}" for run in tied
        )
        print(f"Tied for best within the {args.noise} noise floor: {names}")
        print("Breaking the tie on elapsed time, which is measured exactly:")
        for run in sorted(tied, key=lambda r: harness_facts(r).get("elapsed") or 1e9):
            facts = harness_facts(run)
            print(f"  {run["_name"]:28} {run['summary']['mean']}/5  {facts.get('elapsed')}s")
    default = min(tied, key=lambda r: harness_facts(r).get("elapsed") or 1e9)
    default_model = default["_name"]
    print(
        f"\nDefault (OPENAI_MODEL): {default_model} — "
        f"{default['summary']['mean']}/5 at {harness_facts(default).get('elapsed')}s"
    )

    pins: dict[str, str] = {}
    for agent in agents:
        values = {model: scores[model].get(agent) for model in models}
        base = values.get(default_model)
        winner, best = None, None
        for model, value in values.items():
            if value is not None and (best is None or value > best):
                winner, best = model, value
        if winner and base is not None and winner != default_model and best - base > args.noise:
            pins[agent] = winner

    if pins:
        print("\nPin these — they beat the default by more than the noise floor:")
        for agent, model in pins.items():
            gap = scores[model][agent] - scores[default_model][agent]
            print(f"  {agent:32} -> {model:22} (+{gap:.2f})")
        print("\n  AGENT_MODELS=" + ",".join(f"{a}={m}" for a, m in pins.items()))
    else:
        print(
            f"\nPin nothing. No agent beats {default_model} by more than the "
            f"{args.noise} noise floor, so a per-agent fleet would be choosing "
            "between models the judge cannot reliably tell apart — at the cost "
            "of more moving parts and the slowest model's latency on some "
            "requests. One model for everything is the honest choice here."
        )
    print(
        "\nVerify any pin by re-running the harness and the judge with it set. A "
        "single-pass screening gap is weaker evidence than a repeat-3 confirmation."
    )
    return 0


def decision(values: dict[str, float | None], noise: float) -> str:
    present = [(model, value) for model, value in values.items() if value is not None]
    if len(present) < 2:
        return "not enough data"
    ranked = sorted(present, key=lambda kv: -kv[1])
    gap = ranked[0][1] - ranked[1][1]
    if gap <= noise:
        return f"too close to call (gap {gap:.2f})"
    return f"{ranked[0][0]} by {gap:.2f}"


if __name__ == "__main__":
    raise SystemExit(main())
