"""Migration harness: build a 0001-era SQLite DB with legacy rows, upgrade to
head, then assert the domain/agent split preserved every row.

Usage::

    .venv/bin/python scripts/check_migration.py

It works on a throwaway file under ``/tmp`` so the dev database is never touched.
"""

from __future__ import annotations

import json
import os
import subprocess
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("MIGRATION_DB", "/tmp/cpa_migration_check.db"))
URL = f"sqlite:///{DB_PATH}"

FAILURES: list[str] = []


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


def seed_legacy(conn: sqlite3.Connection) -> dict[str, str]:
    """Insert 0001-era rows whose ``agent_type`` holds a bare domain."""
    now = datetime.now(timezone.utc).isoformat(" ")
    ids = {
        "user": str(uuid.uuid4()),
        "agent_profile": str(uuid.uuid4()),
        "conversation": str(uuid.uuid4()),
        "message": str(uuid.uuid4()),
        "memory": str(uuid.uuid4()),
        "feedback": str(uuid.uuid4()),
    }
    conn.execute(
        "INSERT INTO users (id, email, name, password_hash, is_active, is_superuser,"
        " created_at, updated_at) VALUES (?,?,?,?,1,0,?,?)",
        (ids["user"], "legacy@example.com", "Legacy User", "x" * 20, now, now),
    )
    conn.execute(
        "INSERT INTO agent_profiles (id, user_id, agent_type, profile_data,"
        " is_configured, interaction_count, revision, created_at, updated_at)"
        " VALUES (?,?,?,?,1,7,3,?,?)",
        (
            ids["agent_profile"],
            ids["user"],
            "education",
            json.dumps({"board": "CBSE", "class_level": "10"}),
            now,
            now,
        ),
    )
    conn.execute(
        "INSERT INTO conversations (id, user_id, agent_type, title, is_archived,"
        " message_count, meta, created_at, updated_at) VALUES (?,?,?,?,0,2,?,?,?)",
        (
            ids["conversation"],
            ids["user"],
            "marketing",
            "Legacy campaign",
            json.dumps({"source": "legacy"}),
            now,
            now,
        ),
    )
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, agent_type,"
        " meta, created_at) VALUES (?,?,?,?,?,?,?)",
        (
            ids["message"],
            ids["conversation"],
            "assistant",
            "Legacy answer body",
            "marketing",
            json.dumps({"provider": "ollama"}),
            now,
        ),
    )
    conn.execute(
        "INSERT INTO memories (id, user_id, agent_type, content, embedding, kind,"
        " importance, occurrences, use_count, is_active, meta,"
        " created_at, updated_at) VALUES (?,?,?,?,?,?,?,1,0,1,?,?,?)",
        (
            ids["memory"],
            ids["user"],
            "technical",
            "Prefers Python examples",
            json.dumps([0.01] * 8),
            "preference",
            0.8,
            json.dumps({}),
            now,
            now,
        ),
    )
    conn.execute(
        "INSERT INTO feedback (id, user_id, message_id, conversation_id, agent_type,"
        " rating, feedback_text, processed, outcome, created_at)"
        " VALUES (?,?,?,?,?,?,?,0,?,?)",
        (
            ids["feedback"],
            ids["user"],
            ids["message"],
            ids["conversation"],
            "analytics",
            1,
            "ok",
            json.dumps({}),
            now,
        ),
    )
    # A row that is already fully qualified: the domain must be *derived*, not
    # defaulted, which exercises the substr/split_part branch.
    ids["memory_qualified"] = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO memories (id, user_id, agent_type, content, embedding, kind,"
        " importance, occurrences, use_count, is_active, meta,"
        " created_at, updated_at) VALUES (?,?,?,?,?,?,?,1,0,1,?,?,?)",
        (
            ids["memory_qualified"],
            ids["user"],
            "creative.poster-image",
            "Likes bold typography",
            json.dumps([0.02] * 8),
            "preference",
            0.6,
            json.dumps({}),
            now,
            now,
        ),
    )
    # A global-scope memory (agent_type NULL) must stay unscoped.
    ids["memory_global"] = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO memories (id, user_id, agent_type, content, embedding, kind,"
        " importance, occurrences, use_count, is_active, meta,"
        " created_at, updated_at) VALUES (?,?,NULL,?,?,?,?,1,0,1,?,?,?)",
        (
            ids["memory_global"],
            ids["user"],
            "Based in Pune",
            json.dumps([0.03] * 8),
            "fact",
            0.9,
            json.dumps({}),
            now,
            now,
        ),
    )
    conn.commit()
    return ids


def main() -> int:
    if DB_PATH.exists():
        DB_PATH.unlink()
    for suffix in ("-wal", "-shm"):
        side = Path(str(DB_PATH) + suffix)
        if side.exists():
            side.unlink()

    print(f"database: {DB_PATH}")
    print("\n1. upgrade to 0001_initial")
    alembic("upgrade", "0001_initial")
    conn = sqlite3.connect(DB_PATH)
    version = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    check("stamped 0001_initial", version == "0001_initial", version)

    print("\n2. insert legacy rows (agent_type = bare domain)")
    ids = seed_legacy(conn)
    conn.close()
    print("   inserted users/agent_profiles/conversations/messages/memories/feedback")

    print("\n3. upgrade head")
    proc = alembic("upgrade", "head")
    printed = [ln for ln in proc.stderr.splitlines() if "Running upgrade" in ln]
    for line in printed:
        print("   " + line.strip())

    print("\n4. verify schema + data")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    version = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    check("stamped 0002_domain_agent", version == "0002_domain_agent", version)

    tables = {
        r["name"]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    check("domain_profiles table exists", "domain_profiles" in tables)

    for table in ("agent_profiles", "conversations", "memories", "feedback"):
        cols = {
            r["name"] for r in conn.execute(f"PRAGMA table_info({table})")
        }
        check(f"{table}.agent_key", "agent_key" in cols)
        check(f"{table}.domain", "domain" in cols)
        check(f"{table} dropped agent_type", "agent_type" not in cols)

    row = conn.execute("SELECT * FROM agent_profiles").fetchone()
    check(
        "agent_profiles migrated education -> education.class10-maths",
        row["agent_key"] == "education.class10-maths" and row["domain"] == "education",
        f"{row['agent_key']} / {row['domain']}",
    )
    check(
        "agent_profiles kept profile_data + revision",
        json.loads(row["profile_data"])["board"] == "CBSE" and row["revision"] == 3,
    )
    check("agent_profiles.last_used_at added", "last_used_at" in row.keys())

    row = conn.execute("SELECT * FROM conversations").fetchone()
    check(
        "conversations migrated marketing -> marketing.social-copy",
        row["agent_key"] == "marketing.social-copy" and row["domain"] == "marketing",
        f"{row['agent_key']} / {row['domain']}",
    )
    check("conversations kept title", row["title"] == "Legacy campaign")

    row = conn.execute("SELECT * FROM messages").fetchone()
    check(
        "messages migrated agent_key",
        row["agent_key"] == "marketing.social-copy",
        row["agent_key"],
    )
    check("messages.output_kind defaults to text", row["output_kind"] == "text", row["output_kind"])
    check("messages.media defaults to []", json.loads(row["media"]) == [], row["media"])
    check("messages kept content", row["content"] == "Legacy answer body")

    def memory(row_id: str) -> sqlite3.Row:
        return conn.execute("SELECT * FROM memories WHERE id = ?", (row_id,)).fetchone()

    row = memory(ids["memory"])
    check(
        "memories migrated technical -> technical.python",
        row["agent_key"] == "technical.python" and row["domain"] == "technical",
        f"{row['agent_key']} / {row['domain']}",
    )
    check("memories kept embedding", len(json.loads(row["embedding"])) == 8)

    row = memory(ids["memory_qualified"])
    check(
        "already-qualified key keeps agent_key, derives domain",
        row["agent_key"] == "creative.poster-image" and row["domain"] == "creative",
        f"{row['agent_key']} / {row['domain']}",
    )

    row = memory(ids["memory_global"])
    check(
        "global memory stays unscoped (agent_key + domain NULL)",
        row["agent_key"] is None and row["domain"] is None,
        f"{row['agent_key']} / {row['domain']}",
    )

    row = conn.execute("SELECT * FROM feedback").fetchone()
    check(
        "feedback migrated analytics -> analytics.eda-planner",
        row["agent_key"] == "analytics.eda-planner" and row["domain"] == "analytics",
        f"{row['agent_key']} / {row['domain']}",
    )
    check("feedback kept feedback_text", row["feedback_text"] == "ok")

    indexes = {
        r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
    }
    expected_indexes = {
        "ix_agent_profiles_agent_key",
        "ix_agent_profiles_domain",
        "ix_conversations_agent_key",
        "ix_conversations_domain",
        "ix_memories_agent_key",
        "ix_memories_domain",
        "ix_memories_user_agent",
        "ix_memories_user_domain",
        "ix_feedback_agent_key",
        "ix_feedback_domain",
        "ix_domain_profiles_domain",
        "ix_domain_profiles_user_id",
    }
    for name in sorted(expected_indexes):
        check(f"{name} created", name in indexes)
    stale = {n for n in indexes if n.endswith("_agent_type")}
    check("no stale ix_*_agent_type indexes", not stale, ", ".join(sorted(stale)))

    uniques = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_profiles'"
    ).fetchone()["sql"]
    check(
        "uq_agent_profiles_user_agent on (user_id, agent_key)",
        "uq_agent_profiles_user_agent" in uniques and "agent_key" in uniques,
    )
    conn.close()

    print("\n5. downgrade back to 0001_initial")
    alembic("downgrade", "0001_initial")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    version = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    check("downgrade stamped 0001_initial", version == "0001_initial", version)
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(conversations)")}
    check("downgrade restored agent_type", "agent_type" in cols and "domain" not in cols)
    tables = {
        r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    check("downgrade dropped domain_profiles", "domain_profiles" not in tables)
    conn.close()

    print("\n6. re-upgrade head then alembic check (models vs migrations)")
    alembic("upgrade", "head")
    env = {**os.environ, "DATABASE_URL": URL, "PYTHONPATH": str(BACKEND)}
    proc = subprocess.run(
        [sys.executable, "-m", "alembic", "check"],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
    )
    combined = (proc.stdout + proc.stderr).strip()
    check("alembic check clean", proc.returncode == 0, combined.splitlines()[-1] if combined else "")

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL MIGRATION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
