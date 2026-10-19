#!/usr/bin/env python
"""Compare two evaluation reports, assertion by assertion.

Only runs produced with the same provider and model are worth comparing, so the
configuration of both is printed and any difference is called out.

    python scripts/marketing_eval/compare.py BASELINE AFTER
    python scripts/marketing_eval/compare.py            # the two most recent
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPORTS = Path(__file__).resolve().parent / "reports"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pick(pattern: str) -> Path:
    matches = sorted(REPORTS.glob(f"*{pattern}*.json"))
    if not matches:
        raise SystemExit(f"No report matching {pattern!r} in {REPORTS}")
    return matches[-1]


def assertions(report: dict) -> dict[tuple[str, str], tuple[bool, str]]:
    out: dict[tuple[str, str], tuple[bool, str]] = {}
    for case in report["cases"]:
        for item in case["assertions"]:
            out[(case["id"], item["label"])] = (item["passed"], item.get("detail", ""))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", nargs="?", default="BASELINE")
    parser.add_argument("after", nargs="?", default="AFTER")
    args = parser.parse_args()

    before_path, after_path = pick(args.before), pick(args.after)
    before, after = load(before_path), load(after_path)

    print(f"before : {before_path.name}")
    print(f"after  : {after_path.name}")
    print()

    cfg_b, cfg_a = before["configuration"], after["configuration"]
    comparable = cfg_b.get("llm_provider") == cfg_a.get("llm_provider") and cfg_b.get(
        "llm_model"
    ) == cfg_a.get("llm_model")
    print(f"{'setting':<26}{'before':<28}{'after':<28}")
    print("-" * 82)
    for key in sorted(set(cfg_b) | set(cfg_a)):
        b, a = str(cfg_b.get(key)), str(cfg_a.get(key))
        flag = "" if b == a else "   <-- changed"
        print(f"{key:<26}{b:<28}{a:<28}{flag}")
    if not comparable:
        print("\n!! Different provider or model — these runs are NOT comparable.")
    print()

    tb, ta = before["totals"], after["totals"]
    print(f"{'metric':<24}{'before':>10}{'after':>10}{'delta':>10}")
    print("-" * 54)
    for key in ("cases", "assertions", "passed", "failed", "errors", "skipped"):
        b, a = tb.get(key, 0), ta.get(key, 0)
        print(f"{key:<24}{b:>10}{a:>10}{a - b:>+10}")

    ab, aa = assertions(before), assertions(after)

    fixed = sorted(k for k in ab.keys() & aa.keys() if not ab[k][0] and aa[k][0])
    broke = sorted(k for k in ab.keys() & aa.keys() if ab[k][0] and not aa[k][0])
    still = sorted(k for k in ab.keys() & aa.keys() if not ab[k][0] and not aa[k][0])
    added = sorted(k for k in aa.keys() - ab.keys())
    removed = sorted(k for k in ab.keys() - aa.keys())

    def show(title: str, keys: list, source: dict) -> None:
        if not keys:
            return
        print(f"\n{title} ({len(keys)})")
        for case_id, label in keys:
            detail = source.get((case_id, label), (None, ""))[1]
            print(f"  {case_id:34s} {label}" + (f" → {detail}" if detail else ""))

    show("FIXED", fixed, aa)
    show("REGRESSED", broke, aa)
    show("STILL FAILING", still, aa)
    show("NEW assertions (added to the dataset)", added, aa)
    show("REMOVED assertions", removed, ab)

    # Latency, per case, for the generating cases only.
    lat_b = {c["id"]: c["latency_ms"] for c in before["cases"] if c["latency_ms"] > 1000}
    lat_a = {c["id"]: c["latency_ms"] for c in after["cases"] if c["latency_ms"] > 1000}
    shared = sorted(lat_b.keys() & lat_a.keys())
    if shared:
        total_b = sum(lat_b[k] for k in shared)
        total_a = sum(lat_a[k] for k in shared)
        print(
            f"\nlatency over {len(shared)} generating cases: "
            f"{total_b / 1000:.0f}s → {total_a / 1000:.0f}s "
            f"({(total_a - total_b) / 1000:+.0f}s)"
        )

    print("\n" + "=" * 54)
    verdict = "no regressions" if not broke else f"{len(broke)} REGRESSION(S)"
    print(f"{len(fixed)} fixed · {len(still)} still failing · {verdict}")
    print("=" * 54)
    return 1 if broke else 0


if __name__ == "__main__":
    sys.exit(main())
