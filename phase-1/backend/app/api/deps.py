"""Shared API dependencies: auth guard, DB session, catalog key validation."""

from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.agents.catalog import (
    DOMAIN_ORDER,
    UnknownAgentError,
    UnknownDomainError,
    get_agent_spec,
    get_domain,
)
from app.core.http import HTTP_422_UNPROCESSABLE
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve and validate the bearer token; every protected route uses this."""
    if credentials is None or not credentials.credentials:
        raise CREDENTIALS_EXCEPTION

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWTError as exc:
        raise CREDENTIALS_EXCEPTION from exc

    if payload.get("type") != "access":
        raise CREDENTIALS_EXCEPTION

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (TypeError, ValueError) as exc:
        raise CREDENTIALS_EXCEPTION from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise CREDENTIALS_EXCEPTION
    return user


def validate_domain(
    domain: Annotated[str, Path(description="Domain key, e.g. 'education'")],
) -> str:
    try:
        return get_domain(domain).key
    except UnknownDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown domain '{domain}'. Valid domains: {', '.join(DOMAIN_ORDER)}",
        ) from exc


def validate_agent(
    agent_key: Annotated[
        str, Path(description="Agent key, e.g. 'marketing.post-image'")
    ],
) -> str:
    try:
        return get_agent_spec(agent_key).key
    except UnknownAgentError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Unknown agent '{agent_key}'. Agent keys look like "
                f"'<domain>.<slug>' — see GET /api/agents."
            ),
        ) from exc


def resolve_agent_key(value: str | None) -> str | None:
    """Validate an agent key supplied in a body or query, not a path."""
    if value is None:
        return None
    try:
        return get_agent_spec(value).key
    except UnknownAgentError as exc:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE, detail=f"Unknown agent '{value}'"
        ) from exc


def resolve_domain_key(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return get_domain(value).key
    except UnknownDomainError as exc:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE, detail=f"Unknown domain '{value}'"
        ) from exc


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
DomainKey = Annotated[str, Depends(validate_domain)]
AgentKey = Annotated[str, Depends(validate_agent)]
