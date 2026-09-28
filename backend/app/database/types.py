"""Dialect-portable column types.

The application targets PostgreSQL + pgvector. To keep the stack runnable in a
constrained development environment (no Docker / no Postgres), the same models
also work on SQLite: ``JSONB`` degrades to ``JSON`` and the vector column
degrades to a JSON array of floats (similarity is then computed in Python).
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator

from app.core.config import settings

# ``JSONB`` on PostgreSQL, plain ``JSON`` elsewhere.
JSONBType = JSON().with_variant(JSONB(astext_type=Text()), "postgresql")


class Embedding(TypeDecorator):
    """Vector column: ``vector(N)`` on PostgreSQL, JSON array elsewhere."""

    impl = JSON
    cache_ok = True

    def __init__(self, dim: int | None = None, **kwargs: Any) -> None:
        self.dim = dim or settings.EMBEDDING_DIM
        super().__init__(**kwargs)

    def load_dialect_impl(self, dialect):  # type: ignore[no-untyped-def]
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dim))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):  # type: ignore[no-untyped-def]
        if value is None:
            return None
        # A plain list of floats is accepted by both pgvector and the JSON impl.
        return [float(component) for component in value]

    def process_result_value(self, value, dialect):  # type: ignore[no-untyped-def]
        if value is None:
            return None
        if isinstance(value, str):  # defensive: some drivers hand back text
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = [float(x) for x in value.strip("[]").split(",") if x.strip()]
        return [float(component) for component in value]
