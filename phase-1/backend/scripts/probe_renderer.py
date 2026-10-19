#!/usr/bin/env python
"""Read-only probe of the local card renderer across every declared size.

Part of the Phase 2 marketing audit. Renders the exact size options the
marketing agents advertise (post-image platforms, ad-creative ad sizes) with a
realistic spec, and reports geometry facts that reveal layout failures:

  * where the headline block starts and ends vertically
  * whether the CTA pill overlaps the text stack
  * the final fitted font size (a size at the floor means the text was squeezed)
  * whether the headline had to be truncated to fit max_lines

Nothing in app/ is modified. Output goes to /tmp so generated_media stays clean.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from app.agents.catalog import get_agent_spec  # noqa: E402
from app.media.base import ImageSpec  # noqa: E402
from app.media.card_renderer import _fit_text, _wrap  # noqa: E402
from app.media.fonts import load_font, scalable_fonts_available  # noqa: E402

BRAND = ["#4F46E5", "#0F172A"]

# A realistic, on-spec payload: 7-word headline, 11-word subline, offer, CTA.
SPEC_FIELDS = dict(
    headline="Cut Your Cloud Bill By Thirty Percent",
    subline="Automated rightsizing finds idle capacity your team forgot about",
    badge="30% OFF",
    cta="Start free trial",
    logo_text="ACME CLOUD",
    alt_text="",
)


def geometry(spec: ImageSpec) -> dict:
    """Recompute the renderer's layout maths without drawing, to inspect it."""
    spec = spec.sanitized()
    width, height = spec.width, spec.height
    canvas = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(canvas)

    margin = max(40, round(min(width, height) * 0.085))
    content_width = width - margin * 2

    blocks = []
    if spec.badge:
        badge_size = max(14, round(height * 0.030))
        blocks.append(("badge", 1, round(badge_size * 2.3), badge_size))

    headline_start = round(height * 0.135) if height >= 400 else round(height * 0.30)
    headline_min = max(18, round(height * 0.05))
    headline_lines, headline_font, headline_lh = _fit_text(
        draw,
        spec.headline,
        max_width=content_width,
        max_height=round(height * 0.52),
        start_size=headline_start,
        min_size=headline_min,
        bold=True,
        max_lines=4,
    )
    blocks.append(("headline", len(headline_lines), headline_lh, getattr(headline_font, "size", 0)))

    if spec.subline:
        sub_lines, sub_font, sub_lh = _fit_text(
            draw,
            spec.subline,
            max_width=content_width,
            max_height=round(height * 0.22),
            start_size=round(height * 0.052) if height >= 400 else round(height * 0.12),
            min_size=max(13, round(height * 0.028)),
            bold=False,
            max_lines=3,
        )
        blocks.append(("subline", len(sub_lines), sub_lh, getattr(sub_font, "size", 0)))

    total = 0
    for index, (kind, count, line_height, _size) in enumerate(blocks):
        total += line_height * count
        if index < len(blocks) - 1:
            total += round(height * (0.035 if kind == "badge" else 0.030))

    cta_height = round(height * 0.11) if spec.cta else 0
    y = max(margin, (height - total - cta_height) // 2)
    stack_top = y
    for index, (kind, count, line_height, _size) in enumerate(blocks):
        if kind == "badge":
            y += line_height + round(height * 0.035)
            continue
        y += line_height * count
        if index < len(blocks) - 1:
            y += round(height * 0.030)
    stack_bottom = y

    # The CTA pill, as _draw_cta computes it.
    cta_top = cta_bottom = None
    if spec.cta:
        cta_font = load_font(max(14, round(height * 0.032)), bold=True)
        pad_y = round(height * 0.020)
        box_height = getattr(cta_font, "size", 16) + pad_y * 2
        cta_bottom = height - margin
        cta_top = cta_bottom - box_height

    # Did the headline lose words? _fit_text truncates to max_lines at the floor.
    floor_font = load_font(headline_min, bold=True)
    full_lines = _wrap(draw, spec.headline, floor_font, content_width)
    truncated = len(headline_lines) < len(full_lines) and getattr(
        headline_font, "size", 0
    ) <= headline_min

    return {
        "canvas": f"{width}x{height}",
        "margin": margin,
        "headline_size": getattr(headline_font, "size", 0),
        "headline_floor": headline_min,
        "at_floor": getattr(headline_font, "size", 0) <= headline_min,
        "headline_lines": len(headline_lines),
        "stack_top": stack_top,
        "stack_bottom": stack_bottom,
        "overflows_canvas": stack_bottom > height,
        "cta_top": cta_top,
        "cta_overlaps_text": bool(cta_top is not None and stack_bottom > cta_top),
        "truncated": truncated,
        "rendered_headline": " / ".join(headline_lines),
    }


def main() -> int:
    print(f"scalable fonts available: {scalable_fonts_available()}")

    cases: list[tuple[str, str, int, int]] = []
    for agent_key in ("marketing.post-image", "marketing.ad-creative"):
        spec = get_agent_spec(agent_key)
        for label, (w, h) in spec.options.get("sizes", {}).items():
            cases.append((agent_key.split(".")[1], label, int(w), int(h)))

    header = (
        f"{'agent':<12}{'size option':<22}{'canvas':<12}{'font':>5}"
        f"{'floor':>6}{'lines':>6}{'stack':>12}{'overflow':>9}{'cta clash':>10}{'cut':>5}"
    )
    print("\n" + header)
    print("-" * len(header))

    problems: list[str] = []
    for agent, label, width, height in cases:
        spec = ImageSpec(**SPEC_FIELDS, brand_colors=list(BRAND), width=width, height=height)
        info = geometry(spec)
        flags = []
        if info["overflows_canvas"]:
            flags.append("overflow")
        if info["cta_overlaps_text"]:
            flags.append("cta-overlap")
        if info["truncated"]:
            flags.append("headline-truncated")
        if flags:
            problems.append(f"{agent} / {label} ({width}x{height}): {', '.join(flags)}")

        print(
            f"{agent:<12}{label:<22}{info['canvas']:<12}"
            f"{info['headline_size']:>5}{info['headline_floor']:>6}"
            f"{info['headline_lines']:>6}"
            f"{str(info['stack_top']) + '-' + str(info['stack_bottom']):>12}"
            f"{('YES' if info['overflows_canvas'] else '-'):>9}"
            f"{('YES' if info['cta_overlaps_text'] else '-'):>10}"
            f"{('YES' if info['truncated'] else '-'):>5}"
        )

    print()
    if problems:
        print(f"{len(problems)} size option(s) produce broken layouts:")
        for item in problems:
            print(f"  - {item}")
    else:
        print("no layout problems detected at any declared size")

    # Render the worst case so it can be looked at.
    print("\nrendering the two smallest canvases to /tmp for inspection:")
    from app.media.card_renderer import LocalCardRenderer

    renderer = LocalCardRenderer()
    for label, width, height in (("leaderboard", 728, 90), ("linkedin", 1200, 627)):
        spec = ImageSpec(**SPEC_FIELDS, brand_colors=list(BRAND), width=width, height=height)
        media = renderer.render(spec, filename_hint=f"probe-{label}")
        from app.media.storage import media_path

        source = media_path(media.filename)
        target = Path(f"/tmp/probe-{label}.png")
        target.write_bytes(source.read_bytes())
        source.unlink(missing_ok=True)
        print(f"  {target}  ({media.width}x{media.height}, {media.bytes_written} bytes)")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
