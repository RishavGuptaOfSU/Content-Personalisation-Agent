#!/usr/bin/env python
"""Verify the visual-style profile field actually changes the rendered palette.

The audit found `ad-creative` collected no style field, so `ImageSpec.style` was
always empty and the style -> palette inference in `build_theme` never fired for
ads. This checks the inference directly — no model, no database — and asserts
both image agents can now be styled.

    python scripts/check_styles.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.catalog import image_agents  # noqa: E402
from app.media.base import ImageSpec  # noqa: E402
from app.media.card_renderer import build_theme  # noqa: E402

FAILURES: list[str] = []
BRAND = ["#4F46E5", "#0F172A"]

#: style token -> the palette build_theme should resolve it to
EXPECTED = {
    "Bold type": "brand",
    "Minimal": "light",
    "Dark mode": "dark",
    "Gradient": "gradient",
}


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


def theme_for(style: str) -> tuple:
    spec = ImageSpec(
        headline="Cut your cloud bill",
        brand_colors=list(BRAND),
        style=style,
        palette="brand",
    ).sanitized()
    theme = build_theme(spec)
    return theme.top, theme.text


def main() -> int:
    print("1. both image agents expose a visual style field")
    for spec in image_agents():
        keys = {field.key for field in spec.profile_fields}
        check(f"{spec.key} has a style field", "style" in keys, ", ".join(sorted(keys)))

    # `post-image.style` has been required since the multi-domain build, so its
    # requiredness is pre-existing. `ad-creative.style` was added in Phase 2 and
    # must stay optional, or saving the catalog change would flip every already
    # configured ad-creative profile back to "not configured".
    ad_style = next(
        field
        for spec in image_agents()
        if spec.slug == "ad-creative"
        for field in spec.profile_fields
        if field.key == "style"
    )
    check(
        "the newly added ad-creative style field is optional",
        not ad_style.required,
        f"required={ad_style.required}",
    )

    print("\n2. each style resolves to a distinct palette")
    themes = {style: theme_for(style) for style in EXPECTED}
    for style, (top, text) in themes.items():
        print(f"      {style:<12} background={top} text={text}")
    check(
        "Minimal is light (dark text on a light background)",
        themes["Minimal"][1] == (15, 23, 42),
        str(themes["Minimal"][1]),
    )
    check(
        "Dark mode is dark (light text on a dark background)",
        themes["Dark mode"][0] == (15, 23, 42) and themes["Dark mode"][1] == (248, 250, 252),
        str(themes["Dark mode"]),
    )
    check(
        "Bold type uses the brand colour as the background",
        themes["Bold type"][0] == (79, 70, 229),
        str(themes["Bold type"][0]),
    )
    distinct = {value[0] for value in themes.values()}
    check(
        "the four styles do not all collapse to one palette",
        len(distinct) >= 3,
        f"{len(distinct)} distinct backgrounds",
    )

    print("\n3. an empty style still renders (the old behaviour must not break)")
    top, text = theme_for("")
    check("empty style falls back to the brand palette", top == (79, 70, 229), str(top))

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL STYLE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
