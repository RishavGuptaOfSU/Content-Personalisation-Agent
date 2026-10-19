"""Hosted image generation through an OpenAI-compatible images API.

Selected with ``IMAGE_PROVIDER=openai``. Used when a photographic or illustrative
image is wanted rather than the local typographic card. The agent's JSON spec is
turned into a prompt, so agent code is unchanged either way.
"""

from __future__ import annotations

import base64
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.media.base import BaseImageRenderer, ImageSpec, MediaGenerationError, RenderedMedia
from app.media.storage import build_filename, media_path, prune_media, public_url

logger = get_logger(__name__)

#: The API accepts a fixed set of sizes; map to the nearest by aspect ratio.
_SUPPORTED = ((1024, 1024), (1536, 1024), (1024, 1536))


def _nearest_size(width: int, height: int) -> tuple[int, int]:
    target = width / max(height, 1)
    return min(_SUPPORTED, key=lambda size: abs(size[0] / size[1] - target))


def build_prompt(spec: ImageSpec) -> str:
    """Turn the structured spec into an image prompt."""
    parts = [
        f'A polished social media graphic. Primary headline text: "{spec.headline}".',
    ]
    if spec.subline:
        parts.append(f'Secondary line: "{spec.subline}".')
    if spec.badge:
        parts.append(f'Small tag reading "{spec.badge}".')
    if spec.cta:
        parts.append(f'A button labelled "{spec.cta}".')
    if spec.brand_colors:
        parts.append(f"Brand colours: {', '.join(spec.brand_colors[:3])}.")
    if spec.style:
        parts.append(f"Visual style: {spec.style}.")
    parts.append(
        f"{spec.palette} palette, {spec.layout} composition, clean modern typography, "
        "high contrast, no watermark, no lorem ipsum, spell all text exactly as given."
    )
    return " ".join(parts)


class OpenAIImageRenderer(BaseImageRenderer):
    name = "openai-images"

    def render(self, spec: ImageSpec, *, filename_hint: str = "image") -> RenderedMedia:
        spec = spec.sanitized()
        if not settings.OPENAI_API_KEY:
            raise MediaGenerationError(
                "IMAGE_PROVIDER=openai but OPENAI_API_KEY is not set."
            )

        width, height = _nearest_size(spec.width, spec.height)
        payload: dict[str, Any] = {
            "model": settings.OPENAI_IMAGE_MODEL,
            "prompt": build_prompt(spec),
            "size": f"{width}x{height}",
            "n": 1,
        }

        try:
            with httpx.Client(timeout=settings.OPENAI_IMAGE_TIMEOUT) as client:
                response = client.post(
                    f"{settings.OPENAI_BASE_URL.rstrip('/')}/images/generations",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                )
        except httpx.HTTPError as exc:
            raise MediaGenerationError(f"Image API unreachable: {exc}") from exc

        if response.status_code >= 400:
            raise MediaGenerationError(
                f"Image API returned HTTP {response.status_code}: {response.text[:300]}"
            )

        items = response.json().get("data") or []
        if not items:
            raise MediaGenerationError("Image API returned no images.")
        item = items[0]

        if item.get("b64_json"):
            content = base64.b64decode(item["b64_json"])
        elif item.get("url"):
            try:
                with httpx.Client(timeout=settings.OPENAI_IMAGE_TIMEOUT) as client:
                    content = client.get(item["url"]).content
            except httpx.HTTPError as exc:
                raise MediaGenerationError(f"Could not download the image: {exc}") from exc
        else:
            raise MediaGenerationError("Image API response contained no image payload.")

        filename = build_filename(filename_hint)
        path = media_path(filename)
        path.write_bytes(content)
        prune_media()

        logger.info("Generated %s via %s (%dx%d)", filename, self.name, width, height)
        return RenderedMedia(
            filename=filename,
            url=public_url(filename),
            media_type="image",
            mime_type="image/png",
            width=width,
            height=height,
            bytes_written=len(content),
            alt_text=spec.alt_text or f"Generated graphic: {spec.headline}",
            renderer=self.name,
            spec={"prompt": payload["prompt"], "model": settings.OPENAI_IMAGE_MODEL},
        )

    def health(self) -> dict[str, Any]:
        return {
            "renderer": self.name,
            "model": settings.OPENAI_IMAGE_MODEL,
            "api_key_configured": bool(settings.OPENAI_API_KEY),
            "ok": bool(settings.OPENAI_API_KEY),
        }
