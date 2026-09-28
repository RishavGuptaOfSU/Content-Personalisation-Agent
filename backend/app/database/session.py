"""Engine / session factory plus schema bootstrap."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _engine_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {"echo": settings.SQL_ECHO, "future": True, "pool_pre_ping": True}
    if settings.is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_size"] = settings.DB_POOL_SIZE
        kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    return kwargs


engine: Engine = create_engine(settings.DATABASE_URL, **_engine_kwargs())

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


if settings.is_sqlite:

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _record):  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a transactional session."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ensure_pgvector_extension() -> bool:
    """Create the ``vector`` extension when running on PostgreSQL."""
    if not settings.is_postgres:
        return False
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension is available")
        return True
    except Exception as exc:  # pragma: no cover - depends on DB privileges
        logger.warning("Could not create pgvector extension: %s", exc)
        return False


def create_vector_index() -> None:
    """Create an ANN index on ``memories.embedding`` (PostgreSQL only)."""
    if not settings.is_postgres:
        return
    statement = text(
        "CREATE INDEX IF NOT EXISTS ix_memories_embedding_cosine "
        "ON memories USING hnsw (embedding vector_cosine_ops)"
    )
    try:
        with engine.begin() as connection:
            connection.execute(statement)
    except Exception as exc:  # pragma: no cover
        logger.warning("Skipping vector index creation: %s", exc)


def init_db() -> None:
    """Create the extension + all tables. Idempotent and safe at startup."""
    from app import models  # noqa: F401  (register mappers)
    from app.database.base import Base

    ensure_pgvector_extension()
    Base.metadata.create_all(bind=engine)
    create_vector_index()
    logger.info("Database schema ready (%s)", engine.dialect.name)
