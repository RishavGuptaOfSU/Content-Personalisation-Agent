"""HTTP status compatibility shims.

Starlette renamed ``HTTP_422_UNPROCESSABLE_ENTITY`` to
``HTTP_422_UNPROCESSABLE_CONTENT`` (RFC 9110 wording) and deprecated the old
name. Resolving it once here keeps the routes warning-free on both versions.
"""

from __future__ import annotations

from fastapi import status

HTTP_422_UNPROCESSABLE: int = int(
    getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)
)

__all__ = ["HTTP_422_UNPROCESSABLE"]
