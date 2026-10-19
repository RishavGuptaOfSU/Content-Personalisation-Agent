"""Media generation: image and chart rendering for visual agents."""

from __future__ import annotations

from threading import Lock
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.media.base import (
    BaseImageRenderer,
    ChartSeries,
    ChartSpec,
    ImageSpec,
    MediaGenerationError,
    RenderedMedia,
)
from app.media.card_renderer import LocalCardRenderer
from app.media.chart_renderer import ChartRenderer, get_chart_renderer
from app.media.storage import media_path, media_root, prune_media, public_url

logger = get_logger(__name__)

_lock = Lock()
_image_renderer: BaseImageRenderer | None = None


def get_image_renderer() -> BaseImageRenderer:
    """The configured image renderer (``IMAGE_PROVIDER``), built lazily."""
    global _image_renderer
    if _image_renderer is None:
        with _lock:
            if _image_renderer is None:
                if settings.IMAGE_PROVIDER == "openai":
                    try:
                        from app.media.openai_images import OpenAIImageRenderer

                        _image_renderer = OpenAIImageRenderer()
                    except Exception as exc:  # pragma: no cover
                        logger.error(
                            "Could not initialise the OpenAI image renderer (%s); "
                            "falling back to local card rendering.",
                            exc,
                        )
                        _image_renderer = LocalCardRenderer()
                else:
                    _image_renderer = LocalCardRenderer()
                logger.info("Image renderer: %s", _image_renderer.name)
    return _image_renderer


def reset_renderers() -> None:
    """Testing hook."""
    global _image_renderer
    with _lock:
        _image_renderer = None


def media_status() -> dict[str, Any]:
    return {
        "image": get_image_renderer().health(),
        "chart": {"renderer": get_chart_renderer().name, "ok": True},
        "configured_image_provider": settings.IMAGE_PROVIDER,
        "media_root": str(media_root()),
        "retention_files": settings.MEDIA_MAX_FILES,
    }


__all__ = [
    "BaseImageRenderer",
    "ChartRenderer",
    "ChartSeries",
    "ChartSpec",
    "ImageSpec",
    "LocalCardRenderer",
    "MediaGenerationError",
    "RenderedMedia",
    "get_chart_renderer",
    "get_image_renderer",
    "media_path",
    "media_root",
    "media_status",
    "prune_media",
    "public_url",
    "reset_renderers",
]
