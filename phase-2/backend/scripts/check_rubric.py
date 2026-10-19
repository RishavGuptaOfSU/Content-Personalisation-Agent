#!/usr/bin/env python
"""Checks rubric.md parses, and that it agrees with cases.toml both ways.

Two failure modes this exists to catch:

* a case declares a dimension the rubric never defines — the judge would have
  no anchors to score against
* the rubric defines a dimension no case declares — dead prose that looks like
  it is being measured when nothing ever scores it

Neither shows up at runtime, which is exactly why they need a check.

    python scripts/check_rubric.py
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from scripts.marketing_eval.rubric import (  # noqa: E402
    ANCHOR_LEVELS,
    SCALE_LEVELS,
    RubricError,
    load_rubric,
)

CASES_FILE = HERE / "marketing_eval" / "cases.toml"

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


def main() -> int:
    print("1. rubric.md parses")
    try:
        rubric = load_rubric()
    except RubricError as exc:
        print(f"  [FAIL] load_rubric() -> {exc}")
        return 1
    check("dimensions found", len(rubric) > 0, str(len(rubric)))
    check(
        "the 1-5 scale is described in full",
        sorted(rubric.scale) == list(SCALE_LEVELS),
        str(sorted(rubric.scale)),
    )
    check("a brand context is stated", "Acme Cloud" in rubric.brand_note)
    check(
        "the banned terms are stated",
        "clickbait" in rubric.brand_note and "emojis" in rubric.brand_note,
        rubric.brand_note[:80] + "...",
    )

    print("\n2. every dimension has a full set of anchors")
    for name, dim in rubric.dimensions.items():
        complete = sorted(dim.anchors) == list(ANCHOR_LEVELS) and all(
            text.strip() for text in dim.anchors.values()
        )
        check(f"`{name}` ({dim.group})", complete)

    print("\n3. the brand context matches what the harness actually configures")
    from scripts.marketing_eval.harness import BRAND

    for value in (BRAND["brand_name"], BRAND["tone"], *BRAND["avoid"]):
        check(
            f"rubric mentions {value!r}",
            str(value).lower() in rubric.brand_note.lower(),
        )
    check(
        "rubric names the audience the harness sets",
        all(str(a).lower() in rubric.brand_note.lower() for a in BRAND["audience"]),
        ", ".join(BRAND["audience"]),
    )

    print("\n4. every dimension a case declares exists in the rubric")
    cases = tomllib.loads(CASES_FILE.read_text(encoding="utf-8"))["case"]
    declared: dict[str, list[str]] = {}
    for case in cases:
        for name in case.get("rubric", []):
            declared.setdefault(name, []).append(case["id"])
    for name, case_ids in sorted(declared.items()):
        check(
            f"`{name}` is defined",
            name in rubric,
            f"{len(case_ids)} case(s)",
        )

    print("\n5. every dimension in the rubric is declared by some case")
    for name in rubric.names():
        check(f"`{name}` is used", name in declared, ", ".join(declared.get(name, []))[:60])

    print("\n6. each case's dimensions are unique and scorable")
    for case in cases:
        names = case.get("rubric", [])
        if not names:
            continue
        check(f"{case['id']}: no duplicate dimensions", len(names) == len(set(names)))
    # A handoff or a routing decision has no creative output to judge: the
    # deterministic assertion ("did it hand off to the right agent") is the
    # whole test. Every case that *does* produce content must be scorable,
    # otherwise it silently escapes qualitative review.
    unscored_categories = {"out_of_scope", "routing"}
    for case in cases:
        has_dims = bool(case.get("rubric"))
        generative = case["category"] not in unscored_categories
        if generative:
            check(f"{case['id']}: generative case is scorable", has_dims)
        else:
            check(
                f"{case['id']}: {case['category']} case needs no dimensions",
                not has_dims,
                "" if not has_dims else f"declares {case['rubric']}",
            )

    print("\n7. the parsed anchors render into a prompt block")
    sample = rubric.get(sorted(rubric.names())[0])
    block = sample.prompt_block()
    check(
        "a dimension renders with all three anchors",
        all(f"{level} = " in block for level in ANCHOR_LEVELS),
        block.splitlines()[0],
    )
    check("the scale renders", all(f"{level} = " in rubric.scale_block() for level in SCALE_LEVELS))

    print("\n8. the dimensions a text judge must skip are declared and real")
    check(
        "at least one visual-only dimension is declared",
        len(rubric.visual_only) > 0,
        ", ".join(sorted(rubric.visual_only)),
    )
    for name in sorted(rubric.visual_only):
        check(f"`{name}` is a defined dimension", name in rubric)
        check(
            f"`{name}` belongs to a visual group",
            "image" in rubric.get(name).group.lower(),
            rubric.get(name).group,
        )
    image_case = next(c for c in cases if c["id"] == "image-ordinary-linkedin")
    scorable, skipped = rubric.judgeable(image_case["rubric"])
    check(
        "an image case splits into scorable and skipped",
        bool(scorable) and bool(skipped),
        f"score {scorable}, skip {skipped}",
    )
    check(
        "nothing is both scored and skipped",
        not (set(scorable) & set(skipped)),
    )
    check(
        "the split loses no dimension",
        sorted(scorable + skipped) == sorted(image_case["rubric"]),
    )
    copy_case = next(c for c in cases if c["id"] == "copy-ordinary-linkedin")
    check(
        "a text case skips nothing",
        rubric.judgeable(copy_case["rubric"])[1] == [],
    )
    try:
        rubric.judgeable(["not_a_real_dimension"])
    except RubricError:
        check("an unknown dimension is rejected by judgeable()", True)
    else:
        check("an unknown dimension is rejected by judgeable()", False)

    print("\n9. a broken rubric fails loudly instead of parsing into nonsense")
    good = rubric.source.read_text(encoding="utf-8")
    broken = {
        "a missing anchor cell": good.replace(
            "| `hook` | Opens with a definition or the product name |",
            "| `hook` |  |",
        ),
        "a dimension name that is not backticked": good.replace("| `hook` |", "| hook |"),
        "a duplicated dimension": good.replace(
            "### Image agents",
            "| `hook` | a | b | c |\n\n### Image agents",
        ),
        "a missing scale level": good.replace("**4** — usable as-is with a tweak.\n", ""),
        "no brand blockquote": "\n".join(
            line for line in good.splitlines() if not line.strip().startswith(">")
        ),
        "no Dimensions section": good.replace(
            "## Dimensions\n", "## Something Else\n", 1
        ),
        "a skip-list entry that is not a dimension": good.replace(
            "- `legibility` —", "- `not_a_dimension` —"
        ),
    }
    tmp = Path("/tmp/_rubric_negative.md")
    try:
        for label, text in broken.items():
            tmp.write_text(text, encoding="utf-8")
            try:
                load_rubric(tmp)
            except RubricError:
                check(f"rejects {label}", True)
            except Exception as exc:  # noqa: BLE001
                check(f"rejects {label}", False, f"raised {type(exc).__name__}, not RubricError")
            else:
                check(f"rejects {label}", False, "parsed without complaint")
        # And the unmodified file still parses, so the harness above is sound.
        tmp.write_text(good, encoding="utf-8")
        check("still accepts the real rubric", len(load_rubric(tmp)) == len(rubric))
    finally:
        tmp.unlink(missing_ok=True)

    print(f"\n{len(rubric)} dimensions across {len(rubric.groups())} groups, "
          f"{len(cases)} cases")
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL RUBRIC CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
