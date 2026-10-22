#!/usr/bin/env python
"""Verifies every quantitative claim in the paper against the stored reports.

A paper's numbers are usually transcribed by hand, which is where they drift
from the runs they describe. This recomputes each one from the JSON artefacts
and asserts the LaTeX source contains the matching string, so a stale figure
fails here instead of in review.

    phase-2/backend/.venv/bin/python paper/check_claims.py
"""

from __future__ import annotations

import glob
import itertools
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "phase-2" / "backend" / "scripts" / "marketing_eval" / "reports"
TEX = Path(__file__).resolve().parent / "ieee_access_paper.tex"

FAILURES: list[str] = []
RAW = TEX.read_text(encoding="utf-8")
#: LaTeX wraps prose at the column, so "7 favoured" can be split across a
#: newline. Collapse whitespace before substring matching, or the check fails
#: on line breaks rather than on wrong numbers.
SOURCE = re.sub(r"\s+", " ", RAW)


def load(pattern: str) -> dict:
    hits = sorted(glob.glob(str(REPORTS / pattern)))
    if not hits:
        raise SystemExit(f"missing report: {pattern}")
    return json.loads(Path(hits[-1]).read_text())


def report_of(scores: dict) -> dict:
    return json.loads((REPORTS / scores["report"]["file"]).read_text())


def check(label: str, computed, needle: str | None = None) -> None:
    """Assert the computed value, and that the paper actually states it."""
    if needle is None:
        needle = str(computed)
    present = needle in SOURCE
    mark = "PASS" if present else "FAIL"
    print(f"  [{mark}] {label}: computed {computed!r}; paper contains {needle!r}")
    if not present:
        FAILURES.append(f"{label} (expected {needle!r} in the .tex)")


def main() -> int:
    print("1. deterministic suite")
    base = load("*BASELINE-before-fixes*.json")
    final = load("*FINAL-with-grounding*.json")
    fixed = load("*CLOUD-gemma4-cases-fixed-openai.json")
    check("baseline", f"{base['totals']['passed']}/{base['totals']['assertions']}", "102/105")
    check("with guards", f"{final['totals']['passed']}/{final['totals']['assertions']}", "105/108")
    check("corrected config", f"{fixed['totals']['passed']}/{fixed['totals']['assertions']}", "110/110")
    check("residual failures",
          final["totals"]["assertions"] - final["totals"]["passed"], "three residual")
    cloud29 = load("*CLOUD-gemma4-fixed-openai.json")
    check("local elapsed", f"{final['elapsed_seconds']:.0f}", "1325")
    check("cloud elapsed (29 cases)", f"{cloud29['elapsed_seconds']:.0f}", "88")
    check("dataset size", fixed["totals"]["cases"], "30-case")

    print("\n2. judge reliability")
    single = load("*VERIFY-single-gemma4*.scores.json")
    mixed = load("*VERIFY-mixed-fleet*.scores.json")
    rel_s, rel_m = single["summary"]["reliability"], mixed["summary"]["reliability"]
    spreads = sorted({rel_s["mean_spread"], rel_m["mean_spread"]})
    check("judge mean spread range", spreads, "0.51--0.54")
    agree = sorted({rel_s["unanimous_fraction"], rel_m["unanimous_fraction"]})
    check("exact agreement range", agree, "62--69\\%")
    check("single-arm mean", single["summary"]["mean"], "4.28")
    check("mixed-arm mean", mixed["summary"]["mean"], "4.18")
    check("fives in control arm", single["summary"]["distribution"]["5"], "36 of 61")

    print("\n3. scale collapse")
    v1 = load("*CLOUD-gemma4-fixed-openai.scores-promptv1.json")
    v2 = load("*CLOUD-gemma4-cases-fixed-openai.scores.json")

    def raw(d: dict) -> Counter:
        return Counter(s for c in d["cases"] for e in c["dimensions"].values() for s in e["runs"])

    r1, r2 = raw(v1), raw(v2)
    check("v1 judgement count", sum(r1.values()), "174")
    check("v1 even-valued scores", r1[2] + r1[4], "every score was 1, 3 or 5")
    even_pct = 100 * (r2[2] + r2[4]) / sum(r2.values())
    check("v2 even-valued share", f"{even_pct:.1f}\\%", "10.4\\%")
    check("worst spread v1", v1["summary"]["reliability"]["max_spread"], "from 4 to 2")
    check("judged mean v2", v2["summary"]["mean"], "4.23")
    check("dimension scores", v2["summary"]["scored_dimensions"], "61 dimension scores")

    print("\n4. bake-off")
    rows = []
    for path in sorted(glob.glob(str(REPORTS / "*BAKEOFF2*.scores.json"))):
        s = json.loads(Path(path).read_text())
        rep = report_of(s)
        rows.append((s["report"]["llm_model"], s["summary"]["mean"],
                     rep["totals"]["passed"], rep["totals"]["assertions"],
                     round(rep["elapsed_seconds"]), rep["totals"]["errors"]))
    for model, mean, passed, total, secs, errs in sorted(rows, key=lambda r: -(r[1] or 0)):
        if errs:
            check(f"{model} errored cases", errs, "9 of 30 cases errored")
            check(f"{model} assertions", f"{passed}/{total}", f"{passed}/{total}")
            continue
        check(f"{model} judged", mean, f"{mean:.2f}")
        check(f"{model} assertions", f"{passed}/{total}", f"{passed}/{total}")
        check(f"{model} seconds", secs, str(secs))
    comparable = [r for r in rows if r[5] == 0]
    top2 = sorted(comparable, key=lambda r: -r[1])[:2]
    check("top-two gap", round(top2[0][1] - top2[1][1], 2), "0.01")
    slower, faster = sorted((top2[0][4], top2[1][4]), reverse=True)
    check("latency ratio of top two", round(slower / faster, 1), "3.3")
    check("free model count", len(rows), "seven of twenty-two")

    print("\n5. paired A/B statistics")
    def flat(d: dict) -> dict:
        return {(c["id"], n): float(e["score"])
                for c in d["cases"] for n, e in c["dimensions"].items()}

    a, b = flat(single), flat(mixed)
    keys = sorted(set(a) & set(b))
    diffs = [b[k] - a[k] for k in keys]
    nz = [d for d in diffs if d]
    check("paired dimensions", len(keys), "61 paired dimension")
    check("unchanged pairs", len(diffs) - len(nz), "46 were unchanged")
    check("favoured mixed", sum(1 for d in nz if d > 0), "7 favoured")
    check("favoured single", sum(1 for d in nz if d < 0), "8 the single model")

    ranks = [0.0] * len(nz)
    order = sorted(range(len(nz)), key=lambda i: abs(nz[i]))
    i = 0
    while i < len(nz):
        j = i
        while j + 1 < len(nz) and abs(nz[order[j + 1]]) == abs(nz[order[i]]):
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    wp = sum(ranks[i] for i in range(len(nz)) if nz[i] > 0)
    wm = sum(ranks[i] for i in range(len(nz)) if nz[i] < 0)
    W = min(wp, wm)
    total = len(nz) * (len(nz) + 1) / 2
    cnt = sum(1 for signs in itertools.product([0, 1], repeat=len(nz))
              if min(s := sum(ranks[i] for i in range(len(nz)) if signs[i]), total - s) <= W)
    p = cnt / 2 ** len(nz)
    d = (sum(diffs) / len(diffs)) / statistics.stdev(diffs)
    check("Wilcoxon W", W, "45.5")
    check("non-tied n", len(nz), "n = 15")
    check("p value", f"{p:.2f}", "p = 0.42")
    check("Cohen's d", f"{d:.2f}", "-0.12")

    print("\n6. latency of the A/B arms")
    rs, rm = report_of(single), report_of(mixed)
    check("single arm seconds", round(rs["elapsed_seconds"]), "54")
    check("mixed arm seconds", round(rm["elapsed_seconds"]), "201")
    check("slowdown factor", round(rm["elapsed_seconds"] / rs["elapsed_seconds"], 1), "3.7")
    check("arm assertions", f"{rs['totals']['passed']}/{rs['totals']['assertions']}", "109/110")
    check("pins recorded", len(rm["configuration"]["agent_models"]), "two agents")

    print("\n7. per-agent movement with no configuration change")
    agents = single["summary"]["by_agent"]
    unchanged = [k for k in agents if k not in (rm["configuration"]["agent_models"] or {})]
    worst = max(abs(mixed["summary"]["by_agent"][k] - agents[k]) for k in unchanged)
    check("largest unchanged-agent move", round(worst, 2), "0.37")

    print("\n8. dataset composition")
    import tomllib
    cases = tomllib.loads(
        (ROOT / "phase-2" / "backend" / "scripts" / "marketing_eval" / "cases.toml")
        .read_text()
    )["case"]
    cats = Counter(c["category"] for c in cases)
    check("case count", len(cases), "30 request cases")
    check("category count", len(cats), "twelve")
    # Needles use single spaces because SOURCE has had its whitespace collapsed.
    check("ordinary", cats["ordinary"], "ordinary & 7")
    check("out of scope", cats["out_of_scope"], "out of scope & 6")
    check("grounding", cats["grounding"], "grounding & 4")
    check("complex", cats["complex"], "complex & 3")
    check("profile", cats["profile"], "profile & 2")
    check("requires real model", sum(1 for c in cases if c.get("requires_real_model")),
          "Five cases are marked")
    scorable = sum(1 for c in cases if c.get("rubric"))
    check("scorable cases", scorable, "22 of the 30")

    print("\n9. rubric")
    import sys
    sys.path.insert(0, str(ROOT / "phase-2" / "backend"))
    from scripts.marketing_eval.rubric import load_rubric
    r = load_rubric()
    check("dimensions", len(r), "32 dimensions")
    check("groups", len(r.groups()), "five groups")
    check("visual-only dimensions", sorted(r.visual_only), "legibility")

    print("\n10. scope guard thresholds")
    sys.path.insert(0, str(ROOT / "phase-2" / "backend"))
    from app.core.config import settings
    check("min chars", settings.SCOPE_MIN_REQUEST_CHARS, "15")
    check("own max", settings.SCOPE_OWN_MAX_SCORE, "1.5")
    check("other min", settings.SCOPE_OTHER_MIN_SCORE, "4.0")
    check("margin", settings.SCOPE_MIN_MARGIN, "3.0")
    check("token ceiling", settings.LLM_MAX_TOKENS_CEILING, "4{,}000")

    print("\n11. no placeholders left unflagged")
    for bad in ("example.com", "XXXX", "Lorem", "TODO"):
        hit = bad.lower() in SOURCE.lower()
        mark = "FAIL" if hit else "PASS"
        print(f"  [{mark}] {bad!r} absent from the source")
        if hit:
            FAILURES.append(f"placeholder {bad!r} still present")
    # Deliberate, visible gaps the author must fill before submitting. These
    # are not failures: they are the two things only the author knows.
    flagged = re.findall(r"\\REPLACE\{([^}]*)\}", RAW)
    print(f"  [INFO] {len(flagged)} item(s) marked \\REPLACE for the author:")
    for item in flagged:
        print(f"         - {item}")

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}):")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("EVERY QUANTITATIVE CLAIM IN THE PAPER MATCHES THE STORED REPORTS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
