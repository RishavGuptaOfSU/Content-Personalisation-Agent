"""Where generated media is written, and how it is addressed over HTTP."""

from __future__ import annotations

import re
import time
import uuid
from pathlib import Path

from app.core.config import settings

_SAFE = re.compile(r"[^a-z0-9._-]+")


def media_root() -> Path:
    """Directory holding generated files. Created on first use."""
    root = Path(settings.MEDIA_ROOT)
    if not root.is_absolute():
        # Resolve relative to the backend package root so the CWD does not matter.
        root = Path(__file__).resolve().parents[2] / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def build_filename(hint: str, extension: str = "png") -> str:
    """A unique, URL-safe filename that still hints at what produced it."""
    stem = _SAFE.sub("-", str(hint or "media").lower()).strip("-") or "media"
    return f"{stem[:48]}-{int(time.time())}-{uuid.uuid4().hex[:8]}.{extension.lstrip('.')}"


def media_path(filename: str) -> Path:
    """Resolve a filename inside the media root, refusing traversal."""
    root = media_root()
    candidate = (root / Path(filename).name).resolve()
    if candidate.parent != root.resolve():
        raise ValueError("Refusing to resolve a path outside the media root")
    return candidate


def public_url(filename: str) -> str:
    return f"{settings.API_PREFIX}/media/{Path(filename).name}"


def prune_media(max_files: int | None = None) -> int:
    """Delete the oldest generated files beyond the retention cap."""
    limit = max_files if max_files is not None else settings.MEDIA_MAX_FILES
    if limit <= 0:
        return 0
    files = sorted(
        (p for p in media_root().glob("*") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    for path in files[limit:]:
        try:
            path.unlink()
            removed += 1
        except OSError:
            continue
    return removed
