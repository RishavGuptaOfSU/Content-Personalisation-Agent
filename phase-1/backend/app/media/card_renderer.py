"""Local image renderer (Pillow).

Produces real, postable graphics offline: brand-coloured social cards, ad
creatives and posters with wrapped, auto-fitted typography. This is the default
so the image agents work with no API key and no GPU; ``IMAGE_PROVIDER`` can point
at a hosted or diffusion backend instead.
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter

from app.core.logging import get_logger
from app.media.base import BaseImageRenderer, ImageSpec, MediaGenerationError, RenderedMedia
from app.media.fonts import load_font, scalable_fonts_available
from app.media.storage import build_filename, media_path, prune_media, public_url

logger = get_logger(__name__)

RGB = tuple[int, int, int]


@dataclass(slots=True)
class Theme:
    top: RGB
    bottom: RGB
    text: RGB
    muted: RGB
    accent: RGB
    on_accent: RGB


def _hex_to_rgb(value: str, fallback: RGB = (79, 70, 229)) -> RGB:
    text = str(value or "").strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return fallback
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except ValueError:
        return fallback


def _luminance(color: RGB) -> float:
    r, g, b = (channel / 255 for channel in color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _shift(color: RGB, *, lightness: float) -> RGB:
    """Lighten (>1) or darken (<1) a colour in HLS space."""
    r, g, b = (channel / 255 for channel in color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.0, min(1.0, l * lightness))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (round(r * 255), round(g * 255), round(b * 255))


def _readable_on(color: RGB) -> RGB:
    """Black or white, whichever has usable contrast against ``color``."""
    return (17, 24, 39) if _luminance(color) > 0.55 else (255, 255, 255)


def build_theme(spec: ImageSpec) -> Theme:
    """Resolve the palette, honouring the brand colours when supplied."""
    brand = [_hex_to_rgb(value) for value in (spec.brand_colors or []) if value]
    primary = brand[0] if brand else (79, 70, 229)
    secondary = brand[1] if len(brand) > 1 else _shift(primary, lightness=0.55)

    style = (spec.style or "").lower()
    palette = spec.palette
    if palette == "brand" and ("dark" in style or "moody" in style):
        palette = "dark"
    elif palette == "brand" and "minimal" in style:
        palette = "light"
    elif palette == "brand" and ("gradient" in style or "retro" in style):
        palette = "gradient"

    if palette == "dark":
        top, bottom = (15, 23, 42), (2, 6, 23)
        text, muted, accent = (248, 250, 252), (148, 163, 184), primary
    elif palette == "light":
        top, bottom = (248, 250, 252), (226, 232, 240)
        text, muted, accent = (15, 23, 42), (100, 116, 139), primary
    elif palette == "gradient":
        top, bottom = primary, secondary
        text = _readable_on(primary)
        muted = _shift(text, lightness=0.8 if _luminance(text) < 0.5 else 1.2)
        accent = (255, 255, 255) if _luminance(primary) < 0.55 else (17, 24, 39)
    else:  # brand
        top = primary
        bottom = _shift(primary, lightness=0.65)
        text = _readable_on(primary)
        muted = _shift(text, lightness=0.85 if _luminance(text) < 0.5 else 1.15)
        accent = (255, 255, 255) if _luminance(primary) < 0.55 else (17, 24, 39)

    return Theme(
        top=top,
        bottom=bottom,
        text=text,
        muted=muted,
        accent=accent,
        on_accent=_readable_on(accent),
    )


def _vertical_gradient(size: tuple[int, int], top: RGB, bottom: RGB) -> Image.Image:
    width, height = size
    base = Image.new("RGB", (1, max(height, 2)))
    pixels = base.load()
    for y in range(max(height, 2)):
        ratio = y / max(height - 1, 1)
        pixels[0, y] = tuple(
            round(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3)
        )  # type: ignore[assignment]
    return base.resize((width, height), Image.Resampling.BILINEAR)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = str(text).split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    bold: bool,
    max_lines: int,
) -> tuple[list[str], object, int]:
    """Shrink the font until the wrapped text fits the box."""
    size = start_size
    while size >= min_size:
        font = load_font(size, bold=bold)
        lines = _wrap(draw, text, font, max_width)
        line_height = round(size * 1.18)
        if len(lines) <= max_lines and line_height * len(lines) <= max_height:
            return lines, font, line_height
        size -= max(2, size // 14)
    font = load_font(min_size, bold=bold)
    lines = _wrap(draw, text, font, max_width)[:max_lines]
    return lines, font, round(min_size * 1.18)


class LocalCardRenderer(BaseImageRenderer):
    """Typographic card/poster renderer using Pillow."""

    name = "local-card"

    def render(self, spec: ImageSpec, *, filename_hint: str = "image") -> RenderedMedia:
        spec = spec.sanitized()
        if not spec.headline:
            raise MediaGenerationError("The image specification has no headline to render.")

        # A badge identical to the logo stamp would print the brand twice.
        if spec.badge and spec.logo_text and spec.badge.strip().lower() == spec.logo_text.strip().lower():
            spec.badge = ""

        theme = build_theme(spec)
        width, height = spec.width, spec.height
        canvas = _vertical_gradient((width, height), theme.top, theme.bottom)
        draw = ImageDraw.Draw(canvas)

        self._draw_decoration(canvas, draw, theme, width, height)

        margin = max(40, round(min(width, height) * 0.085))
        content_width = width - margin * 2
        left = margin
        centered = spec.layout == "centered"
        anchor_x = width // 2 if centered else left

        # --- vertical stack -------------------------------------------------
        blocks: list[tuple[str, list[str], object, int, RGB]] = []

        if spec.badge:
            badge_size = max(14, round(height * 0.030))
            badge_font = load_font(badge_size, bold=True)
            # Height of the pill, so the stack below it is not overlapped.
            blocks.append(("badge", [spec.badge], badge_font, round(badge_size * 2.3), theme.text))

        headline_lines, headline_font, headline_lh = _fit_text(
            draw,
            spec.headline,
            max_width=content_width,
            max_height=round(height * 0.52),
            start_size=round(height * 0.135) if height >= 400 else round(height * 0.30),
            min_size=max(18, round(height * 0.05)),
            bold=True,
            max_lines=4,
        )
        blocks.append(("headline", headline_lines, headline_font, headline_lh, theme.text))

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
            blocks.append(("subline", sub_lines, sub_font, sub_lh, theme.muted))

        total = 0
        for index, (kind, lines, _font, line_height, _color) in enumerate(blocks):
            total += line_height * len(lines)
            if index < len(blocks) - 1:
                total += round(height * (0.035 if kind == "badge" else 0.030))

        cta_height = round(height * 0.11) if spec.cta else 0
        y = max(margin, (height - total - cta_height) // 2)

        for index, (kind, lines, font, line_height, color) in enumerate(blocks):
            if kind == "badge":
                self._draw_badge(draw, lines[0], font, anchor_x, y, theme, centered)
                y += line_height + round(height * 0.035)
                continue
            for line in lines:
                draw.text(
                    (anchor_x, y),
                    line,
                    font=font,
                    fill=color,
                    anchor="ma" if centered else "la",
                )
                y += line_height
            if index < len(blocks) - 1:
                y += round(height * 0.030)

        if spec.cta:
            self._draw_cta(draw, spec.cta, theme, anchor_x, height - margin, height, centered)

        if spec.logo_text:
            logo_font = load_font(max(12, round(height * 0.026)), bold=True)
            draw.text(
                (width - margin, margin // 2),
                spec.logo_text.upper(),
                font=logo_font,
                fill=theme.muted,
                anchor="ra",
            )

        filename = build_filename(filename_hint)
        path = media_path(filename)
        canvas.save(path, format="PNG", optimize=True)
        prune_media()

        alt = spec.alt_text or f"Graphic with the headline: {spec.headline}"
        logger.info("Rendered %s (%dx%d) via %s", filename, width, height, self.name)
        return RenderedMedia(
            filename=filename,
            url=public_url(filename),
            media_type="image",
            mime_type="image/png",
            width=width,
            height=height,
            bytes_written=path.stat().st_size,
            alt_text=alt,
            renderer=self.name,
            spec={
                "headline": spec.headline,
                "subline": spec.subline,
                "badge": spec.badge,
                "cta": spec.cta,
                "palette": spec.palette,
                "layout": spec.layout,
                "style": spec.style,
            },
        )

    # ------------------------------------------------------------- internals
    @staticmethod
    def _draw_decoration(
        canvas: Image.Image, draw: ImageDraw.ImageDraw, theme: Theme, width: int, height: int
    ) -> None:
        """A soft accent glow plus a top rule — enough to look designed."""
        radius = round(min(width, height) * 0.55)
        glow = Image.new("RGB", (width, height), tuple(theme.top))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse(
            [width - radius, -radius // 2, width + radius // 2, radius],
            fill=tuple(_shift(theme.top, lightness=1.35)),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(radius=max(12, radius // 6)))
        canvas.paste(Image.blend(canvas.convert("RGB"), glow, alpha=0.35), (0, 0))

        bar = max(3, round(height * 0.008))
        ImageDraw.Draw(canvas).rectangle([0, 0, width, bar], fill=tuple(theme.accent))

    @staticmethod
    def _draw_badge(
        draw: ImageDraw.ImageDraw,
        text: str,
        font,
        anchor_x: int,
        y: int,
        theme: Theme,
        centered: bool,
    ) -> None:
        label = text.upper()
        # Measure the real glyph box: font.size alone ignores ascent/descent and
        # makes the pill outline cut through the letters.
        left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
        text_width = right - left
        text_height = bottom - top
        pad_x = max(14, round(text_height * 0.9))
        pad_y = max(9, round(text_height * 0.55))

        box_width = text_width + pad_x * 2
        box_height = text_height + pad_y * 2
        x0 = anchor_x - box_width / 2 if centered else anchor_x

        draw.rounded_rectangle(
            [x0, y, x0 + box_width, y + box_height],
            radius=round(box_height / 2),
            outline=tuple(theme.muted),
            width=2,
        )
        # Draw from the measured top so the glyphs sit centred inside the pill.
        draw.text(
            (x0 + box_width / 2, y + pad_y - top),
            label,
            font=font,
            fill=tuple(theme.text),
            anchor="ma",
        )

    @staticmethod
    def _draw_cta(
        draw: ImageDraw.ImageDraw,
        text: str,
        theme: Theme,
        anchor_x: int,
        baseline_y: int,
        height: int,
        centered: bool,
    ) -> None:
        font = load_font(max(14, round(height * 0.032)), bold=True)
        pad_x = round(height * 0.030)
        pad_y = round(height * 0.020)
        text_width = draw.textlength(text, font=font)
        text_height = font.size if hasattr(font, "size") else 16
        box_width = text_width + pad_x * 2
        box_height = text_height + pad_y * 2
        x0 = anchor_x - box_width / 2 if centered else anchor_x
        y0 = baseline_y - box_height
        draw.rounded_rectangle(
            [x0, y0, x0 + box_width, y0 + box_height],
            radius=round(box_height / 2),
            fill=tuple(theme.accent),
        )
        draw.text(
            (x0 + box_width / 2, y0 + pad_y),
            text,
            font=font,
            fill=tuple(theme.on_accent),
            anchor="ma",
        )

    def health(self) -> dict[str, object]:
        return {
            "renderer": self.name,
            "ok": True,
            "scalable_fonts": scalable_fonts_available(),
            "note": (
                "Renders typographic cards locally with Pillow — no API key or GPU "
                "required. Set IMAGE_PROVIDER=openai for photographic generation."
            ),
        }
