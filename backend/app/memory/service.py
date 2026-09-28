"""Long-term memory service: write (with dedupe/reinforcement), read, prune."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.embeddings import cosine_similarity
from app.llm.registry import get_embeddings
from app.memory.extractor import MemoryCandidate, get_memory_extractor
from app.memory.vector_store import ScoredMemory, get_vector_store
from app.models.memory import Memory

logger = get_logger(__name__)


class MemoryService:
    """All durable-memory reads and writes go through here."""

    def __init__(self) -> None:
        self._store = get_vector_store()

    # ----------------------------------------------------------------- read
    def embed(self, text: str) -> list[float]:
        return get_embeddings().embed(text)

    def retrieve(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        query: str,
        agent_key: str | None = None,
        domain: str | None = None,
        limit: int | None = None,
        min_similarity: float | None = None,
        mark_used: bool = True,
        include_standing: bool = True,
    ) -> list[ScoredMemory]:
        """Hybrid retrieval for this agent (+ global memories).

        Two complementary signals:

        * **semantic recall** — pgvector cosine search over the request, which
          surfaces topically relevant history; and
        * **standing preferences** — durable, reinforced instructions such as
          "keep posts concise", which must shape *every* response for that agent
          even when they share no vocabulary with the current request.

        Returning only the first would make a learned instruction silently stop
        applying as soon as the user changed subject.
        """
        query = (query or "").strip()
        if not query:
            return []

        embedding = self.embed(query)
        results = self._store.search(
            db,
            user_id=user_id,
            query_embedding=embedding,
            agent_key=agent_key,
            domain=domain,
            limit=limit or settings.MEMORY_TOP_K,
            min_similarity=(
                settings.MEMORY_MIN_SIMILARITY if min_similarity is None else min_similarity
            ),
        )

        if include_standing:
            existing_ids = {scored.memory.id for scored in results}
            for memory in self._standing_preferences(db, user_id, agent_key, domain):
                if memory.id in existing_ids:
                    continue
                similarity = (
                    cosine_similarity(embedding, memory.embedding) if memory.embedding else 0.0
                )
                results.append(ScoredMemory(memory=memory, similarity=similarity, pinned=True))
            results.sort(key=lambda item: item.score, reverse=True)

        if mark_used and results:
            now = datetime.now(UTC)
            for scored in results:
                scored.memory.use_count = (scored.memory.use_count or 0) + 1
                scored.memory.last_used_at = now
            db.flush()

        return results

    def _standing_preferences(
        self,
        db: Session,
        user_id: uuid.UUID,
        agent_key: str | None,
        domain: str | None = None,
    ) -> list[Memory]:
        """Durable instructions that apply to every request in scope."""
        statement = select(Memory).where(
            Memory.user_id == user_id,
            Memory.is_active.is_(True),
            Memory.kind.in_(("preference", "requirement", "feedback")),
        )
        scope = Memory.agent_key.is_(None) & Memory.domain.is_(None)
        if agent_key is not None:
            scope = scope | (Memory.agent_key == agent_key)
        if domain is not None:
            scope = scope | ((Memory.domain == domain) & Memory.agent_key.is_(None))
        statement = statement.where(scope)
        statement = statement.where(
            (Memory.importance >= settings.MEMORY_STANDING_IMPORTANCE)
            | (Memory.occurrences > 1)
        ).order_by(
            Memory.occurrences.desc(), Memory.importance.desc(), Memory.updated_at.desc()
        ).limit(settings.MEMORY_STANDING_LIMIT)
        return list(db.scalars(statement).all())

    def list_memories(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        agent_key: str | None = None,
        domain: str | None = None,
        kind: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_inactive: bool = False,
    ) -> list[Memory]:
        statement = select(Memory).where(Memory.user_id == user_id)
        if agent_key:
            statement = statement.where(Memory.agent_key == agent_key)
        if domain:
            statement = statement.where(Memory.domain == domain)
        if kind:
            statement = statement.where(Memory.kind == kind)
        if not include_inactive:
            statement = statement.where(Memory.is_active.is_(True))
        statement = (
            statement.order_by(Memory.importance.desc(), Memory.created_at.desc())
            .offset(offset)
            .limit(min(limit, 500))
        )
        return list(db.scalars(statement).all())

    def summary(self, db: Session, *, user_id: uuid.UUID) -> dict[str, Any]:
        rows = db.execute(
            select(Memory.agent_key, Memory.domain, Memory.kind, func.count(Memory.id))
            .where(Memory.user_id == user_id, Memory.is_active.is_(True))
            .group_by(Memory.agent_key, Memory.domain, Memory.kind)
        ).all()

        by_agent: dict[str, int] = {}
        by_domain: dict[str, int] = {}
        by_kind: dict[str, int] = {}
        total = 0
        for agent_key, domain, kind, count in rows:
            scope = agent_key or domain or "global"
            by_agent[scope] = by_agent.get(scope, 0) + int(count)
            by_domain[domain or "global"] = by_domain.get(domain or "global", 0) + int(count)
            by_kind[kind] = by_kind.get(kind, 0) + int(count)
            total += int(count)

        return {
            "total": total,
            "by_agent": by_agent,
            "by_domain": by_domain,
            "by_kind": by_kind,
        }

    # ---------------------------------------------------------------- write
    def remember(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        candidate: MemoryCandidate,
        agent_key: str | None = None,
        domain: str | None = None,
        conversation_id: uuid.UUID | None = None,
        extra_meta: dict[str, Any] | None = None,
    ) -> tuple[Memory, bool]:
        """Persist a candidate.

        Returns ``(memory, created)``. A near-duplicate is *reinforced* instead
        of duplicated: occurrences increase and importance rises with a ceiling,
        which is what makes "repeated behaviour" outrank a one-off remark.
        """
        normalized = candidate.normalized()
        if normalized is None:
            raise ValueError("Empty memory candidate")

        scope_agent = agent_key if candidate.agent_scoped else None
        scope_domain = domain if candidate.agent_scoped or domain else None
        embedding = self.embed(normalized.content)

        existing = self._find_duplicate(
            db,
            user_id=user_id,
            agent_key=scope_agent,
            domain=scope_domain,
            embedding=embedding,
            content=normalized.content,
        )
        if existing is not None:
            existing.occurrences = (existing.occurrences or 1) + 1
            existing.importance = min(1.0, (existing.importance or 0.5) + 0.08)
            existing.is_active = True
            existing.updated_at = datetime.now(UTC)
            meta = dict(existing.meta or {})
            meta["reinforced_at"] = datetime.now(UTC).isoformat()
            meta["occurrences"] = existing.occurrences
            existing.meta = meta
            db.flush()
            logger.debug("Reinforced memory %s (n=%d)", existing.id, existing.occurrences)
            return existing, False

        meta = dict(normalized.meta)
        if extra_meta:
            meta.update(extra_meta)

        memory = Memory(
            user_id=user_id,
            agent_key=scope_agent,
            domain=scope_domain,
            content=normalized.content,
            embedding=embedding,
            kind=normalized.kind,
            importance=normalized.importance,
            occurrences=1,
            meta=meta,
            source_conversation_id=conversation_id,
        )
        db.add(memory)
        db.flush()
        self._prune(db, user_id=user_id, agent_key=scope_agent, domain=scope_domain)
        logger.debug("Stored memory %s: %s", memory.id, memory.content[:60])
        return memory, True

    def remember_many(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        candidates: list[MemoryCandidate],
        agent_key: str | None = None,
        domain: str | None = None,
        conversation_id: uuid.UUID | None = None,
        extra_meta: dict[str, Any] | None = None,
    ) -> list[Memory]:
        created: list[Memory] = []
        for candidate in candidates:
            try:
                memory, is_new = self.remember(
                    db,
                    user_id=user_id,
                    candidate=candidate,
                    agent_key=agent_key,
                    domain=domain,
                    conversation_id=conversation_id,
                    extra_meta=extra_meta,
                )
            except ValueError:
                continue
            if is_new:
                created.append(memory)
        return created

    def capture_from_message(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        agent_key: str,
        domain: str | None = None,
        message: str = "",
        conversation_id: uuid.UUID | None = None,
        message_id: uuid.UUID | None = None,
    ) -> list[Memory]:
        """Extract + persist durable memories from a single user turn."""
        candidates = get_memory_extractor().from_message(message, agent_key)
        if not candidates:
            return []
        return self.remember_many(
            db,
            user_id=user_id,
            candidates=candidates,
            agent_key=agent_key,
            domain=domain,
            conversation_id=conversation_id,
            extra_meta={"source_message_id": str(message_id) if message_id else None},
        )

    def deactivate(self, db: Session, *, user_id: uuid.UUID, memory_id: uuid.UUID) -> bool:
        memory = db.scalar(
            select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        )
        if memory is None:
            return False
        db.delete(memory)
        db.flush()
        return True

    # -------------------------------------------------------------- helpers
    def _find_duplicate(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        agent_key: str | None,
        domain: str | None,
        embedding: list[float],
        content: str,
    ) -> Memory | None:
        statement = select(Memory).where(
            Memory.user_id == user_id,
            Memory.agent_key == agent_key if agent_key else Memory.agent_key.is_(None),
            Memory.domain == domain if domain else Memory.domain.is_(None),
        )
        exact = db.scalar(statement.where(func.lower(Memory.content) == content.lower()))
        if exact is not None:
            return exact

        for memory in db.scalars(statement.order_by(Memory.created_at.desc()).limit(200)).all():
            if not memory.embedding:
                continue
            if cosine_similarity(embedding, memory.embedding) >= settings.MEMORY_DEDUPE_SIMILARITY:
                return memory
        return None

    def _prune(
        self, db: Session, *, user_id: uuid.UUID, agent_key: str | None, domain: str | None = None
    ) -> None:
        """Keep the per-scope memory set bounded; drop the least useful first."""
        statement = select(func.count(Memory.id)).where(
            Memory.user_id == user_id,
            Memory.agent_key == agent_key if agent_key else Memory.agent_key.is_(None),
        )
        total = int(db.scalar(statement) or 0)
        overflow = total - settings.MEMORY_MAX_PER_AGENT
        if overflow <= 0:
            return

        victims = db.scalars(
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.agent_key == agent_key if agent_key else Memory.agent_key.is_(None),
            )
            .order_by(
                Memory.importance.asc(),
                Memory.occurrences.asc(),
                Memory.use_count.asc(),
                Memory.created_at.asc(),
            )
            .limit(overflow)
        ).all()
        for memory in victims:
            db.delete(memory)
        db.flush()


_service: MemoryService | None = None


def get_memory_service() -> MemoryService:
    global _service
    if _service is None:
        _service = MemoryService()
    return _service
