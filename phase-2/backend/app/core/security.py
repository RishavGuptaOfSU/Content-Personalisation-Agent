"""Password hashing and JWT helpers.

``bcrypt`` is used directly (no passlib) to avoid backend-detection issues, and
``PyJWT`` for token encode/decode.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

_MAX_BCRYPT_BYTES = 72  # bcrypt silently truncates beyond this


# --------------------------------------------------------------- passwords
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:_MAX_BCRYPT_BYTES],
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


# ------------------------------------------------------------------ tokens
def create_access_token(
    subject: str | uuid.UUID,
    *,
    expires_minutes: int | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, int]:
    """Return ``(token, expires_in_seconds)``."""
    expire_minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "access",
        "jti": uuid.uuid4().hex,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expire_minutes * 60


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode a JWT. Raises ``jwt.PyJWTError`` on any problem."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "sub"]},
    )
