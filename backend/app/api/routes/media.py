"""Serves generated images and charts.

Files are addressed by the opaque, unguessable filename recorded on the message,
and path traversal is refused by ``media_path``. Kept unauthenticated so the
browser can render ``<img src>`` without attaching a bearer token; the filename
contains a random component and carries no user data.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.media import media_path

router = APIRouter(prefix="/media", tags=["media"])

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


@router.get("/{filename}")
def get_media(filename: str) -> FileResponse:
    try:
        path = media_path(filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid media path"
        ) from exc

    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    suffix = path.suffix.lower()
    return FileResponse(
        path,
        media_type=_MIME.get(suffix, "application/octet-stream"),
        filename=path.name,
        headers={"Cache-Control": "public, max-age=86400"},
    )
