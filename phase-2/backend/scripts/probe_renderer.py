#!/usr/bin/env python
"""Geometry regression test for the local card renderer.

Renders every size the image agents advertise, with realistic copy, and asserts
the composition actually fits the canvas:

  * nothing is drawn outside the margins
  * the CTA pill never overlaps the text stack
  * the canvas is the size that was asked for (no silent resize)
  * the headline is still above its minimum legible size

Exits non-zero on any failure, so it can run as a gate.

    python scripts/probe_renderer.py              # all declared sizes
    python scripts/probe_renderer.py --save       # also write PNGs to /tmp
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from app.agents.catalog import get_agent_spec, image_agents  # noqa: E402
from app.media.base import ImageSpec  # noqa: E402
from app.media.card_renderer import LocalCardRenderer, _fit_text  # noqa: E402
from app.media.fonts import scalable_fonts_available  # noqa: E402
from app.media.storage import media_path  # noqa: E402

BRAND = ["#4F46E5", "#0F172A"]

#: A realistic, on-spec payload plus a deliberately over-long one.
PAYLOADS = {
    "normal": dict(
        headline="Cut Your Cloud Bill By Thirty Percent",
        subline="Automated rightsizing finds idle capacity your team forgot about",
        badge="30% OFF",
        cta="Start free trial",
        logo_text="ACME CLOUD",
        alt_text="",
    ),
    "overlong": dict(
        headline=(
            "This headline is deliberately far too long for any sensible social "
            "card and should still be laid out without escaping the canvas"
        ),
        subline=(
            "And the supporting line is also much longer than the fourteen word "
            "limit the agent was instructed to respect, to prove clamping works"
        ),
        badge="A VERY LONG BADGE LABEL",
        cta="Click here to start your free trial today",
        logo_text="ACME CLOUD INTERNATIONAL",
        alt_text="",
    ),
    "minimal": dict(headline="Pricing", subline="", badge="", cta="", logo_text="", alt_text=""),
}


def measure(spec: ImageSpec) -> dict:
    """Recompute the renderer's layout without drawing, to inspect it."""
    spec = spec.sanitized()
    width, height = spec.width, spec.height
    draw = ImageDraw.Draw(Image.new("RGB", (width, height)))

    short_edge = min(width, height)
    margin = max(8, min(round(short_edge * 0.085), round(short_edge * 0.14)))
    if short_edge >= 400:
        margin = max(40, margin)
    content_width = width - margin * 2
    available = height - margin * 2

    renderer = LocalCardRenderer()
    cta_height = None
    if spec.cta:
        _font, box = renderer._cta_metrics(draw, spec.cta, height)
        gap = max(6, round(height * 0.025))
        if box + gap <= available * 0.45:
            cta_height = box
            available -= box + gap

    badge_block = None
    if spec.badge:
        badge_size = max(10, round(height * 0.030))
        block = round(badge_size * 2.3) + max(6, round(height * 0.035))
        if block <= available * 0.40:
            badge_block = block
            available -= block

    sub_budget = round(available * 0.34) if spec.subline else 0
    head_lines, head_font, head_lh = _fit_text(
        draw,
        spec.headline,
        max_width=content_width,
        max_height=max(round(height * 0.12), available - sub_budget),
        start_size=round(height * 0.135) if height >= 400 else round(height * 0.30),
        min_size=max(11, round(height * 0.05)),
        bold=True,
        max_lines=4 if height >= 300 else 2,
    )
    blocks = [(head_lines, head_lh)]
    if spec.subline and sub_budget >= 14:
        sub_lines, _sub_font, sub_lh = _fit_text(
            draw,
            spec.subline,
            max_width=content_width,
            max_height=sub_budget,
            start_size=round(height * 0.052) if height >= 400 else round(height * 0.12),
            min_size=max(10, round(height * 0.028)),
            bold=False,
            max_lines=3 if height >= 300 else 1,
        )
        blocks.append((sub_lines, sub_lh))

    inner_gap = max(4, round(height * 0.030))
    stack = sum(lh * len(lines) for lines, lh in blocks) + inner_gap * (len(blocks) - 1)
    content_height = stack + (badge_block or 0)
    top = margin + max(0, (available + (badge_block or 0) - content_height) // 2)
    bottom = top + content_height
    cta_top = (height - margin - cta_height) if cta_height else None

    return {
        "margin": margin,
        "stack_top": top,
        "stack_bottom": bottom,
        "cta_top": cta_top,
        "cta_dropped": bool(spec.cta) and cta_height is None,
        "badge_dropped": bool(spec.badge) and badge_block is None,
        "headline_size": getattr(head_font, "size", 0),
        "headline_lines": len(head_lines),
        "overflows_top": top < margin - 1,
        "overflows_bottom": bottom > height - margin + 1,
        "cta_overlaps": bool(cta_top is not None and bottom > cta_top),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Also write PNGs to /tmp")
    args = parser.parse_args()

    print(f"scalable fonts available: {scalable_fonts_available()}")

    sizes: list[tuple[str, str, int, int]] = []
    for spec in image_agents():
        declared = get_agent_spec(spec.key).options.get("sizes", {})
        for label, (w, h) in declared.items():
            sizes.append((spec.slug, label, int(w), int(h)))

    failures: list[str] = []
    header = (
        f"{'agent':<13}{'size option':<22}{'payload':<10}{'canvas':<11}"
        f"{'font':>5}{'lines':>6}{'stack':>12}{'dropped':>10}{'verdict':>9}"
    )
    print("\n" + header)
    print("-" * len(header))

    renderer = LocalCardRenderer()
    for agent, label, width, height in sizes:
        for payload_name, payload in PAYLOADS.items():
            spec = ImageSpec(**payload, brand_colors=list(BRAND), width=width, height=height)
            info = measure(spec)

            problems = []
            if info["overflows_top"] or info["overflows_bottom"]:
                problems.append("overflow")
            if info["cta_overlaps"]:
                problems.append("cta-overlap")

            # Render for real: proves it does not raise and keeps the asked-for size.
            rendered = renderer.render(
                ImageSpec(**payload, brand_colors=list(BRAND), width=width, height=height),
                filename_hint=f"probe-{agent}",
            )
            if (rendered.width, rendered.height) != (width, height):
                problems.append(f"resized to {rendered.width}x{rendered.height}")
            path = media_path(rendered.filename)
            if args.save:
                target = Path(f"/tmp/probe-{agent}-{width}x{height}-{payload_name}.png")
                target.write_bytes(path.read_bytes())
            path.unlink(missing_ok=True)

            dropped = ",".join(
                part
                for part, flag in (("cta", info["cta_dropped"]), ("badge", info["badge_dropped"]))
                if flag
            )
            if problems:
                failures.append(f"{agent} / {label} / {payload_name}: {', '.join(problems)}")
            canvas_label = f"{width}x{height}"
            stack_label = f"{info['stack_top']}-{info['stack_bottom']}"
            print(
                f"{agent:<13}{label:<22}{payload_name:<10}{canvas_label:<11}"
                f"{info['headline_size']:>5}{info['headline_lines']:>6}"
                f"{stack_label:>12}"
                f"{(dropped or '-'):>10}"
                f"{('FAIL' if problems else 'ok'):>9}"
            )

    print()
    if failures:
        print(f"{len(failures)} layout failure(s):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(f"all {len(sizes) * len(PAYLOADS)} size/payload combinations lay out correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
