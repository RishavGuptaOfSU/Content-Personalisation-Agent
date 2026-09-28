"""Font discovery for the local renderer.

matplotlib ships the DejaVu family, so a usable TrueType font is available without
installing system fonts or downloading anything. Falls back through common system
paths, then to Pillow's bitmap default as a last resort.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

from app.core.logging import get_logger

logger = get_logger(__name__)

_CANDIDATES_BOLD = (
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
)
_CANDIDATES_REGULAR = (
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
)


@lru_cache(maxsize=2)
def _font_file(bold: bool) -> str | None:
    """Locate a TrueType file, preferring the one matplotlib bundles."""
    try:
        from matplotlib import font_manager

        wanted = "DejaVu Sans"
        path = font_manager.findfont(
            font_manager.FontProperties(family=wanted, weight="bold" if bold else "normal"),
            fallback_to_default=True,
        )
        if path and Path(path).exists():
            return path
    except Exception as exc:  # pragma: no cover - matplotlib optional at runtime
        logger.debug("matplotlib font lookup failed: %s", exc)

    for candidate in _CANDIDATES_BOLD if bold else _CANDIDATES_REGULAR:
        if Path(candidate).exists():
            return candidate
    return None


@lru_cache(maxsize=64)
def load_font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    """A font at the requested pixel size, cached."""
    path = _font_file(bold)
    if path:
        try:
            return ImageFont.truetype(path, size=max(8, int(size)))
        except OSError as exc:  # pragma: no cover
            logger.warning("Could not load font %s: %s", path, exc)
    # Bitmap fallback: renders, but cannot scale.
    return ImageFont.load_default()


def scalable_fonts_available() -> bool:
    return _font_file(bold=True) is not None
