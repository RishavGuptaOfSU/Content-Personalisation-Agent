#!/usr/bin/env python
"""Re-embed every stored memory with the currently configured provider.

Why this is needed: embeddings from different models live in different vector
spaces. After changing ``EMBEDDING_PROVIDER`` (or the embedding model, or
``EMBEDDING_DIM``), memories embedded by the previous provider will no longer
match anything — semantic recall silently degrades to "nothing found".

    python scripts/reembed_memories.py            # re-embed all
    python scripts/reembed_memories.py --dry-run  # report only
    python scripts/reembed_memories.py --user demo@example.com

On PostgreSQL, changing ``EMBEDDING_DIM`` also changes the column type, so run
an Alembic migration for the new width before re-embedding.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.llm.registry import get_embeddings  # noqa: E402
from app.models import Memory, User  # noqa: E402

BATCH = 32


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-embed stored memories")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    parser.add_argument("--user", help="Limit to one user's email")
    args = parser.parse_args()

    embeddings = get_embeddings()
    print(f"Embedding provider : {embeddings.name}")
    print(f"Target dimension   : {embeddings.dimension}")
    native = getattr(embeddings, "native_dimension", None)
    if native and native != embeddings.dimension:
        print(
            f"  ! model emits {native} dims; EMBEDDING_DIM={embeddings.dimension}. "
            f"Set EMBEDDING_DIM={native} for full fidelity."
        )
    print(f"Database           : {settings.DATABASE_URL.split('@')[-1]}")

    db = SessionLocal()
    try:
        statement = select(Memory).order_by(Memory.created_at.asc())
        if args.user:
            user = db.scalar(select(User).where(User.email == args.user.lower()))
            if user is None:
                print(f"No user with email {args.user!r}")
                return 1
            statement = statement.where(Memory.user_id == user.id)

        memories = list(db.scalars(statement).all())
        print(f"Memories found     : {len(memories)}")
        if not memories:
            return 0

        stale = sum(
            1
            for memory in memories
            if not memory.embedding or len(memory.embedding) != embeddings.dimension
        )
        print(f"Wrong-width vectors: {stale}")

        if args.dry_run:
            print("\nDry run — nothing written.")
            return 0

        updated = 0
        for start in range(0, len(memories), BATCH):
            chunk = memories[start : start + BATCH]
            try:
                vectors = embeddings.embed_many([memory.content for memory in chunk])
            except Exception as exc:
                print(f"\nEmbedding failed at offset {start}: {exc}")
                db.rollback()
                return 1
            for memory, vector in zip(chunk, vectors):
                memory.embedding = vector
                updated += 1
            db.commit()
            print(f"  re-embedded {updated}/{len(memories)}", end="\r", flush=True)

        print(f"\nDone. {updated} memories re-embedded with {embeddings.name}.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
