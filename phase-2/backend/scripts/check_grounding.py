#!/usr/bin/env python
"""Unit checks for the grounding guard — no model, no database, no network.

The guard decides whether a figure in a reply was available to the model. Both
directions matter: it must catch invented claims, and it must not flag figures
the user actually supplied, or legitimate budget allocations, or plain integers
like list numbers and character counts.

    python scripts/check_grounding.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents import grounding  # noqa: E402
from app.agents.catalog import list_agents  # noqa: E402

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


ALL = ["percent", "currency", "multiplier", "upto"]


def main() -> int:  # noqa: PLR0915 - a flat list of cases
    print("1. catches figures the user never supplied")
    supplied = grounding.available_numbers(
        request="Write a LinkedIn post about how much money we save customers"
    )
    for text, expected in [
        ("reduce infrastructure costs by up to 50% compared to on-premise", "50%"),
        ("Unlocking savings of up to $100K per year with Acme Cloud", "$100K"),
        ("teams ship 10x faster with our platform", "10x"),
        ("trusted by up to 5,000 engineering teams", "up to 5,000"),
    ]:
        report = grounding.check(text, supplied=supplied, patterns=ALL)
        check(
            f"flags {expected!r}",
            any(expected.lower() in item.lower() for item in report.unsupported),
            ", ".join(report.unsupported) or "(nothing flagged)",
        )

    print("\n2. accepts figures the user did supply")
    supplied = grounding.available_numbers(
        request="Ad image promoting 30% off annual plans until 31 March"
    )
    report = grounding.check("Get 30% off annual plans", supplied=supplied, patterns=ALL)
    check("does not flag the supplied 30%", report.ok, ", ".join(report.unsupported))

    supplied = grounding.available_numbers(
        request="Plan a campaign", profiles=({"budget": "Medium ($500-5k/mo)"},)
    )
    report = grounding.check("Budget: $500 per month", supplied=supplied, patterns=ALL)
    check(
        "does not flag a figure that came from the profile",
        report.ok,
        ", ".join(report.unsupported),
    )

    print("\n3. allows splitting a budget the user gave")
    supplied = grounding.available_numbers(
        request="Plan a 6 week campaign. Budget is $400 total across the six weeks."
    )
    text = "LinkedIn: $200\nEmail: $100\nBlog: $100"
    report = grounding.check(text, supplied=supplied, patterns=ALL, allow_splits_of=400.0)
    check("a correct $400 split is not flagged", report.ok, ", ".join(report.unsupported))
    report = grounding.check(
        "LinkedIn: $5,000", supplied=supplied, patterns=ALL, allow_splits_of=400.0
    )
    check(
        "an allocation larger than the supplied total IS flagged",
        not report.ok,
        ", ".join(report.unsupported),
    )
    report = grounding.check(text, supplied=supplied, patterns=ALL, allow_splits_of=None)
    check(
        "without the allowance the same split is flagged",
        not report.ok,
        ", ".join(report.unsupported),
    )

    print("\n4. ignores numbers that are not claims")
    supplied = grounding.available_numbers(request="Plan a campaign")
    for text in (
        "1. First post\n2. Second post\n3. Third post",
        "Title tag (58 characters)\nMeta description (142 characters)",
        "Week 1 | Week 2 | Week 3",
        "Post 3 times per week",
    ):
        report = grounding.check(text, supplied=supplied, patterns=ALL)
        check(
            f"plain integers not flagged: {text.splitlines()[0][:34]!r}",
            report.ok,
            ", ".join(report.unsupported),
        )

    print("\n4b. posting cadence is not a claim")
    # Found by the cloud-model eval run: the channel-mix table writes frequency
    # as "3x per week", which the multiplier pattern was flagging as a claim.
    for text in (
        "| LinkedIn | Engineering efficiency | Text posts | 3x per week |",
        "| Email | Direct value | Newsletter | 1x per week |",
        "Publish 2x monthly and 4x / week on X",
        "Cadence: 3X per quarter",
    ):
        report = grounding.check(text, supplied=supplied, patterns=ALL)
        check(
            f"cadence not flagged: {text[:46]!r}", report.ok, ", ".join(report.unsupported)
        )
    # A real multiplier claim must still be caught.
    report = grounding.check("teams ship 10x faster", supplied=supplied, patterns=ALL)
    check("an outcome multiplier IS still flagged", not report.ok, ", ".join(report.unsupported))

    print("\n4c. a figure openly labelled as a proposal is not a fabrication")
    # The campaign planner is instructed to propose a target KPI and label it.
    # Flagging a figure it honestly marked as a suggestion punishes compliance.
    for text in (
        "Increase monthly visits by 20% (suggested figure) to build the funnel.",
        "Guardrail: unsubscribe rate not exceeding 0.5% (suggested figure).",
        "Target $2,000 (estimated) in pipeline.",
        "Reach 5,000 (assumed) impressions.",
    ):
        report = grounding.check(text, supplied=supplied, patterns=ALL)
        check(
            f"labelled proposal not flagged: {text[:46]!r}",
            report.ok,
            ", ".join(report.unsupported),
        )
    # The same figure asserted as fact must still be caught.
    report = grounding.check(
        "We increase monthly visits by 20%.", supplied=supplied, patterns=ALL
    )
    check(
        "the same figure asserted as fact IS flagged",
        not report.ok,
        ", ".join(report.unsupported),
    )

    print("\n5. respects the per-agent pattern list")
    supplied = grounding.available_numbers(request="Plan a campaign")
    report = grounding.check("Allocate $250 across channels", supplied=supplied, patterns=["percent"])
    check("currency ignored when only 'percent' is declared", report.ok)
    report = grounding.check(
        "Allocate $250 across channels", supplied=supplied, patterns=["currency"]
    )
    check("currency caught when declared", not report.ok, ", ".join(report.unsupported))

    print("\n6. the note names the figures")
    report = grounding.check(
        "costs drop 40% and teams ship 3x faster", supplied=set(), patterns=ALL
    )
    note = report.note()
    check("note mentions both figures", "40%" in note and "3x" in note)
    check("note warns it is the model's invention", "invention" in note.lower())

    print("\n7. the catalog declares grounding where it matters")
    for spec in list_agents():
        patterns = spec.options.get("grounding_patterns")
        check(f"{spec.key} declares grounding patterns", bool(patterns), str(patterns))
    planner = next(s for s in list_agents() if s.slug == "campaign-planner")
    check(
        "only the campaign planner may split budgets",
        planner.options.get("allow_budget_splits") is True
        and not any(
            s.options.get("allow_budget_splits")
            for s in list_agents()
            if s.slug != "campaign-planner"
        ),
    )

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL GROUNDING CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
