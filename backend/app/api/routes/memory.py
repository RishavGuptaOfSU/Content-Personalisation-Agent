"""Long-term memory routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.agents.catalog import domain_of
from app.api.deps import CurrentUser, DbSession, resolve_agent_key, resolve_domain_key
from app.memory.extractor import MemoryCandidate
from app.memory.service import get_memory_service
from app.schemas.chat import MemoryCreate, MemoryRead, MemorySummary

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryRead])
def list_memories(
    user: CurrentUser,
    db: DbSession,
    agent_key: str | None = Query(default=None),
    domain: str | None = Query(default=None),
    kind: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[MemoryRead]:
    memories = get_memory_service().list_memories(
        db,
        user_id=user.id,
        agent_key=resolve_agent_key(None if agent_key == "global" else agent_key),
        domain=resolve_domain_key(domain),
        kind=kind,
        limit=limit,
        offset=offset,
    )
    return [MemoryRead.model_validate(memory) for memory in memories]


@router.get("/summary", response_model=MemorySummary)
def memory_summary(
    user: CurrentUser,
    db: DbSession,
    agent_key: str | None = Query(default=None),
    domain: str | None = Query(default=None),
) -> MemorySummary:
    """Counts + the most relevant memories (drives the chat right-hand panel)."""
    service = get_memory_service()
    stats = service.summary(db, user_id=user.id)
    recent = service.list_memories(
        db,
        user_id=user.id,
        agent_key=resolve_agent_key(agent_key),
        domain=resolve_domain_key(domain),
        limit=8,
    )
    return MemorySummary(
        total=stats["total"],
        by_agent=stats["by_agent"],
        by_domain=stats["by_domain"],
        by_kind=stats["by_kind"],
        recent=[MemoryRead.model_validate(memory) for memory in recent],
    )


@router.get("/search", response_model=list[MemoryRead])
def search_memories(
    user: CurrentUser,
    db: DbSession,
    q: str = Query(min_length=2, max_length=500),
    agent_key: str | None = Query(default=None),
    domain: str | None = Query(default=None),
    limit: int = Query(default=8, ge=1, le=50),
) -> list[MemoryRead]:
    """Semantic (vector) search — the same call the pipeline makes."""
    results = get_memory_service().retrieve(
        db,
        user_id=user.id,
        query=q,
        agent_key=resolve_agent_key(agent_key),
        domain=resolve_domain_key(domain),
        limit=limit,
        mark_used=False,
    )
    return [MemoryRead.model_validate(scored.memory) for scored in results]


@router.post("", response_model=MemoryRead, status_code=status.HTTP_201_CREATED)
def create_memory(payload: MemoryCreate, user: CurrentUser, db: DbSession) -> MemoryRead:
    """Let the user teach the system something explicitly."""
    agent_key = resolve_agent_key(
        None if payload.agent_key in (None, "global") else payload.agent_key
    )
    domain = resolve_domain_key(payload.domain)
    # An agent-scoped memory always belongs to that agent's domain, so it also
    # participates in domain-wide retrieval. Derive it rather than asking twice.
    if agent_key and not domain:
        domain = domain_of(agent_key)

    memory, _created = get_memory_service().remember(
        db,
        user_id=user.id,
        candidate=MemoryCandidate(
            content=payload.content,
            kind=payload.kind,
            importance=payload.importance,
            agent_scoped=agent_key is not None or domain is not None,
            source="user",
            meta={"origin": "user"},
        ),
        agent_key=agent_key,
        domain=domain,
    )
    db.commit()
    db.refresh(memory)
    return MemoryRead.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(memory_id: uuid.UUID, user: CurrentUser, db: DbSession) -> None:
    deleted = get_memory_service().deactivate(db, user_id=user.id, memory_id=memory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    db.commit()
