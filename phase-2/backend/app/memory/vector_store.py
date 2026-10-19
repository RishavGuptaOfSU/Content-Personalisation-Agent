"""Semantic memory vector store.

``PgVectorStore`` performs the similarity search inside PostgreSQL using the
pgvector cosine operator (``<=>``) with an HNSW index.

``PortableVectorStore`` is used when the configured database is not PostgreSQL
(the offline development fallback). It loads the candidate rows for the user/agent
and computes cosine similarity in Python. Same interface, same results ordering.
"""

from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.embeddings import cosine_similarity
from app.models.memory import Memory

logger = get_logger(__name__)


@dataclass(slots=True)
class ScoredMemory:
    memory: Memory
    similarity: float
    #: True when the memory was pinned as a standing preference rather than
    #: recalled by topical similarity.
    pinned: bool = False

    @property
    def score(self) -> float:
        """Similarity blended with stored importance (retrieval ranking)."""
        base = 0.75 * self.similarity + 0.25 * (self.memory.importance or 0.0)
        if self.pinned:
            # Standing instructions outrank topical matches; they are the ones
            # the user explicitly asked us to always apply.
            base = max(base, 0.6) + 0.1 * min(self.memory.occurrences or 1, 5)
        return round(base, 6)


class BaseVectorStore(abc.ABC):
    name = "base"

    @abc.abstractmethod
    def search(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        query_embedding: list[float],
        agent_key: str | None = None,
        domain: str | None = None,
        limit: int = 6,
        min_similarity: float = 0.0,
    ) -> list[ScoredMemory]: ...


class PgVectorStore(BaseVectorStore):
    name = "pgvector"

    def search(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        query_embedding: list[float],
        agent_key: str | None = None,
        domain: str | None = None,
        limit: int = 6,
        min_similarity: float = 0.0,
    ) -> list[ScoredMemory]:
        if not query_embedding:
            return []

        vector_literal = "[" + ",".join(f"{value:.7f}" for value in query_embedding) + "]"

        params: dict[str, object] = {
            "user_id": str(user_id),
            "query_vector": vector_literal,
            "limit": limit,
            "min_similarity": min_similarity,
        }
        # Scope: this agent, or the whole domain, or global (both columns NULL).
        clauses = ["agent_key IS NULL AND domain IS NULL"]
        if agent_key is not None:
            clauses.append("agent_key = :agent_key")
            params["agent_key"] = agent_key
        if domain is not None:
            clauses.append("(domain = :domain AND agent_key IS NULL)")
            params["domain"] = domain
        agent_clause = "AND (" + " OR ".join(clauses) + ")"

        statement = text(
            f"""
            SELECT id,
                   1 - (embedding <=> CAST(:query_vector AS vector)) AS similarity
            FROM memories
            WHERE user_id = CAST(:user_id AS uuid)
              AND is_active = TRUE
              AND embedding IS NOT NULL
              {agent_clause}
              AND 1 - (embedding <=> CAST(:query_vector AS vector)) >= :min_similarity
            ORDER BY embedding <=> CAST(:query_vector AS vector)
            LIMIT :limit
            """
        )

        rows = db.execute(statement, params).all()
        if not rows:
            return []

        similarity_by_id = {row.id: float(row.similarity) for row in rows}
        memories = db.scalars(
            select(Memory).where(Memory.id.in_(list(similarity_by_id.keys())))
        ).all()
        scored = [
            ScoredMemory(memory=memory, similarity=similarity_by_id.get(memory.id, 0.0))
            for memory in memories
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored


class PortableVectorStore(BaseVectorStore):
    """Dialect-agnostic fallback (cosine similarity computed in Python)."""

    name = "portable"

    #: Hard cap on rows pulled into memory for scoring.
    candidate_limit = 800

    def search(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        query_embedding: list[float],
        agent_key: str | None = None,
        domain: str | None = None,
        limit: int = 6,
        min_similarity: float = 0.0,
    ) -> list[ScoredMemory]:
        if not query_embedding:
            return []

        statement = select(Memory).where(Memory.user_id == user_id, Memory.is_active.is_(True))
        scope = Memory.agent_key.is_(None) & Memory.domain.is_(None)  # global
        if agent_key is not None:
            scope = scope | (Memory.agent_key == agent_key)
        if domain is not None:
            scope = scope | ((Memory.domain == domain) & Memory.agent_key.is_(None))
        statement = statement.where(scope)
        statement = statement.order_by(Memory.created_at.desc()).limit(self.candidate_limit)

        scored: list[ScoredMemory] = []
        for memory in db.scalars(statement).all():
            if not memory.embedding:
                continue
            similarity = cosine_similarity(query_embedding, memory.embedding)
            if similarity >= min_similarity:
                scored.append(ScoredMemory(memory=memory, similarity=similarity))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]


_store: BaseVectorStore | None = None


def get_vector_store() -> BaseVectorStore:
    """Pick the store implementation that matches the configured database."""
    global _store
    if _store is None:
        _store = PgVectorStore() if settings.is_postgres else PortableVectorStore()
        logger.info("Vector store: %s", _store.name)
    return _store
