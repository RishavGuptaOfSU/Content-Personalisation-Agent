"""Migration harness: upgrade, assert the schema, downgrade, re-upgrade, check.

Phase 2 ships a single squashed migration, so there is no legacy data to
migrate — what matters is that the migration produces exactly the schema the ORM
models declare, and that it reverses cleanly.

    .venv/bin/python scripts/check_migration.py

Works on a throwaway file under ``/tmp`` so the dev database is never touched.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("MIGRATION_DB", "/tmp/marketing_agent_migration_check.db"))
URL = f"sqlite:///{DB_PATH}"

FAILURES: list[str] = []

#: table -> columns that must exist. Guards the columns the product depends on:
#: the agent/domain keys, the brand profile table, and the media payload.
EXPECTED_COLUMNS: dict[str, set[str]] = {
    "users": {"id", "email", "name", "password_hash", "is_active"},
    "global_profiles": {"user_id", "preferred_response_length", "communication_style"},
    "domain_profiles": {"user_id", "domain", "profile_data", "is_configured", "revision"},
    "agent_profiles": {
        "user_id", "agent_key", "domain", "profile_data", "is_configured",
        "interaction_count", "revision", "last_used_at",
    },
    "conversations": {"user_id", "agent_key", "domain", "title", "message_count", "meta"},
    "messages": {"conversation_id", "role", "content", "agent_key", "output_kind", "media", "meta"},
    "memories": {
        "user_id", "agent_key", "domain", "content", "embedding", "kind",
        "importance", "occurrences", "use_count", "is_active",
    },
    "feedback": {"user_id", "agent_key", "domain", "message_id", "rating", "feedback_text", "outcome"},
}

EXPECTED_INDEXES = {
    "ix_users_email",
    "ix_domain_profiles_user_id",
    "ix_domain_profiles_domain",
    "ix_agent_profiles_agent_key",
    "ix_agent_profiles_domain",
    "ix_conversations_agent_key",
    "ix_conversations_domain",
    "ix_messages_conversation_id",
    "ix_memories_agent_key",
    "ix_memories_domain",
    "ix_memories_user_agent",
    "ix_memories_user_domain",
    "ix_feedback_agent_key",
    "ix_feedback_domain",
}


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}{(' -> ' + detail) if detail else ''}")
    if not condition:
        FAILURES.append(label)


def alembic(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DATABASE_URL": URL, "PYTHONPATH": str(BACKEND)}
    proc = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(f"!! alembic {' '.join(args)} failed (exit {proc.returncode})")
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(1)
    return proc


def insert_round_trip(conn: sqlite3.Connection) -> None:
    """Write one row per table so NOT NULL / FK / defaults are exercised."""
    now = datetime.now(timezone.utc).isoformat(" ")
    user_id, conv_id, msg_id = (str(uuid.uuid4()) for _ in range(3))

    conn.execute(
        "INSERT INTO users (id, email, name, password_hash, is_active, is_superuser,"
        " created_at, updated_at) VALUES (?,?,?,?,1,0,?,?)",
        (user_id, "probe@example.com", "Probe", "x" * 20, now, now),
    )
    conn.execute(
        "INSERT INTO domain_profiles (id, user_id, domain, profile_data, is_configured,"
        " revision, created_at, updated_at) VALUES (?,?,?,?,1,1,?,?)",
        (str(uuid.uuid4()), user_id, "marketing", json.dumps({"brand_name": "Acme"}), now, now),
    )
    conn.execute(
        "INSERT INTO agent_profiles (id, user_id, agent_key, domain, profile_data,"
        " is_configured, interaction_count, revision, created_at, updated_at)"
        " VALUES (?,?,?,?,?,1,0,1,?,?)",
        (
            str(uuid.uuid4()), user_id, "marketing.post-image", "marketing",
            json.dumps({"platform": "LinkedIn"}), now, now,
        ),
    )
    conn.execute(
        "INSERT INTO conversations (id, user_id, agent_key, domain, title, is_archived,"
        " message_count, meta, created_at, updated_at) VALUES (?,?,?,?,?,0,1,?,?,?)",
        (
            conv_id, user_id, "marketing.post-image", "marketing", "Probe thread",
            json.dumps({}), now, now,
        ),
    )
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, agent_key, output_kind,"
        " media, meta, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            msg_id, conv_id, "assistant", "Rendered a card", "marketing.post-image", "image",
            json.dumps([{"filename": "x.png", "width": 1200, "height": 627}]),
            json.dumps({"provider": "probe"}), now,
        ),
    )
    conn.execute(
        "INSERT INTO memories (id, user_id, agent_key, domain, content, embedding, kind,"
        " importance, occurrences, use_count, is_active, meta, created_at, updated_at)"
        " VALUES (?,?,?,?,?,?,?,?,1,0,1,?,?,?)",
        (
            str(uuid.uuid4()), user_id, "marketing.post-image", "marketing",
            "Prefers bold type", json.dumps([0.01] * 8), "preference", 0.8,
            json.dumps({}), now, now,
        ),
    )
    conn.execute(
        "INSERT INTO feedback (id, user_id, agent_key, domain, message_id, conversation_id,"
        " rating, feedback_text, processed, outcome, created_at) VALUES (?,?,?,?,?,?,?,?,0,?,?)",
        (
            str(uuid.uuid4()), user_id, "marketing.post-image", "marketing", msg_id, conv_id,
            -1, "too busy", json.dumps({}), now,
        ),
    )
    conn.commit()


def main() -> int:
    for suffix in ("", "-wal", "-shm"):
        side = Path(str(DB_PATH) + suffix)
        if side.exists():
            side.unlink()

    print(f"database: {DB_PATH}")

    print("\n1. upgrade head")
    proc = alembic("upgrade", "head")
    for line in proc.stderr.splitlines():
        if "Running upgrade" in line:
            print("   " + line.strip())

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    version = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    check("stamped 0001_initial", version == "0001_initial", version)

    print("\n2. schema matches what the product needs")
    tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table, columns in EXPECTED_COLUMNS.items():
        check(f"table {table} exists", table in tables)
        if table not in tables:
            continue
        present = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
        missing = columns - present
        check(f"{table} has its required columns", not missing, ", ".join(sorted(missing)))
        stale = {c for c in present if c == "agent_type"}
        check(f"{table} has no legacy agent_type column", not stale)

    indexes = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    missing_indexes = EXPECTED_INDEXES - indexes
    check("all expected indexes created", not missing_indexes, ", ".join(sorted(missing_indexes)))

    uniques = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_profiles'"
    ).fetchone()["sql"]
    check(
        "uq_agent_profiles_user_agent on (user_id, agent_key)",
        "uq_agent_profiles_user_agent" in uniques and "agent_key" in uniques,
    )
    brand_uniques = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='domain_profiles'"
    ).fetchone()["sql"]
    check(
        "uq_domain_profiles_user_domain on (user_id, domain)",
        "uq_domain_profiles_user_domain" in brand_uniques,
    )

    print("\n3. a full row round-trip through every table")
    try:
        insert_round_trip(conn)
        check("inserted one row per table", True)
    except sqlite3.Error as exc:
        check("inserted one row per table", False, str(exc))

    row = conn.execute("SELECT * FROM messages").fetchone()
    if row is not None:
        check("messages.output_kind persisted", row["output_kind"] == "image", row["output_kind"])
        check("messages.media persisted as JSON", json.loads(row["media"])[0]["width"] == 1200)

    print("\n4. cascade delete removes the user's data")
    conn.execute("PRAGMA foreign_keys = ON")
    user_id = conn.execute("SELECT id FROM users").fetchone()["id"]
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    remaining = {
        table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("domain_profiles", "agent_profiles", "conversations", "messages",
                      "memories", "feedback")
    }
    check(
        "deleting the user cascaded everywhere",
        all(count == 0 for count in remaining.values()),
        str(remaining),
    )
    conn.close()

    print("\n5. downgrade to base, then back up")
    alembic("downgrade", "base")
    conn = sqlite3.connect(DB_PATH)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    check(
        "downgrade dropped every application table",
        not (set(EXPECTED_COLUMNS) & tables),
        ", ".join(sorted(set(EXPECTED_COLUMNS) & tables)),
    )
    conn.close()
    alembic("upgrade", "head")

    print("\n6. alembic check (models vs migration)")
    env = {**os.environ, "DATABASE_URL": URL, "PYTHONPATH": str(BACKEND)}
    proc = subprocess.run(
        [sys.executable, "-m", "alembic", "check"],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
    )
    combined = (proc.stdout + proc.stderr).strip()
    check(
        "no drift between the models and the migration",
        proc.returncode == 0,
        combined.splitlines()[-1] if combined else "",
    )

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL MIGRATION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
