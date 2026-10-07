"""Domain → agent split: agent_key + domain everywhere, domain_profiles, message media.

Revision ID: 0002_domain_agent
Revises: 0001_initial
Create Date: 2026-02-01

The catalog changed shape: a domain (``marketing``) now contains many narrow
agents (``marketing.post-image``). Rows written under the old single-level model
stored a bare domain in ``agent_type``; they are migrated to that domain's
default agent so existing conversations, profiles, memories and feedback
survive.

Implementation notes
--------------------
* Every rename happens inside ``batch_alter_table`` so SQLite (which cannot
  ``ALTER ... RENAME COLUMN`` on older versions, nor drop constraints at all)
  goes through table recreation.
* Indexes over ``agent_type`` are dropped *before* the rename and recreated with
  their new names afterwards. Letting batch mode carry them across would keep
  the stale ``ix_*_agent_type`` names and leave ``alembic check`` dirty.
* The ``uq_agent_profiles_user_agent`` unique constraint is deliberately left
  alone: batch mode rewrites it to ``(user_id, agent_key)`` under the same name,
  which is exactly what the ORM declares.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.database.types import JSONBType

revision: str = "0002_domain_agent"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


#: Old bare domain -> the agent that inherits its history.
DEFAULT_AGENT = {
    "education": "education.class10-maths",
    "technical": "technical.python",
    "career": "career.resume-writer",
    "marketing": "marketing.social-copy",
    "analytics": "analytics.eda-planner",
    "research": "research.concept-explainer",
    "creative": "creative.story-writer",
}

#: Domain assigned to rows whose key matched nothing (``domain`` is NOT NULL).
FALLBACK_DOMAIN = "research"


def _is_sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def _split_domain_sql(table: str) -> str:
    """Derive ``domain`` from an already fully qualified ``agent_key``."""
    if _is_sqlite():
        expr = "substr(agent_key, 1, instr(agent_key, '.') - 1)"
    else:
        expr = "split_part(agent_key, '.', 1)"
    return (
        f"UPDATE {table} SET domain = {expr} "
        f"WHERE domain IS NULL AND agent_key LIKE '%.%'"
    )


def _backfill(table: str) -> None:
    """Rewrite bare-domain keys to their default agent and fill ``domain``."""
    for domain, agent_key in DEFAULT_AGENT.items():
        # Both values are module-level literals, never user input.
        op.execute(
            f"UPDATE {table} SET domain = '{domain}', agent_key = '{agent_key}' "
            f"WHERE agent_key = '{domain}'"
        )
    op.execute(_split_domain_sql(table))


def _rename_keys(table: str, *, key_nullable: bool, domain_nullable: bool) -> None:
    """``agent_type`` -> ``agent_key`` (widened) plus a new ``domain`` column."""
    with op.batch_alter_table(table) as batch:
        batch.alter_column(
            "agent_type",
            new_column_name="agent_key",
            existing_type=sa.String(length=32),
            type_=sa.String(length=80),
            existing_nullable=key_nullable,
        )
        batch.add_column(sa.Column("domain", sa.String(length=32), nullable=True))

    _backfill(table)

    if not domain_nullable:
        op.execute(f"UPDATE {table} SET domain = '{FALLBACK_DOMAIN}' WHERE domain IS NULL")
        with op.batch_alter_table(table) as batch:
            batch.alter_column(
                "domain", existing_type=sa.String(length=32), nullable=False
            )


def upgrade() -> None:
    # ------------------------------------------------------- domain_profiles
    op.create_table(
        "domain_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("profile_data", JSONBType, nullable=False),
        sa.Column("is_configured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_domain_profiles_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_domain_profiles"),
        sa.UniqueConstraint("user_id", "domain", name="uq_domain_profiles_user_domain"),
    )
    op.create_index("ix_domain_profiles_user_id", "domain_profiles", ["user_id"])
    op.create_index("ix_domain_profiles_domain", "domain_profiles", ["domain"])

    # --------------------------------------------------------- agent_profiles
    op.drop_index("ix_agent_profiles_agent_type", table_name="agent_profiles")
    _rename_keys("agent_profiles", key_nullable=False, domain_nullable=False)
    with op.batch_alter_table("agent_profiles") as batch:
        batch.add_column(sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_agent_profiles_agent_key", "agent_profiles", ["agent_key"])
    op.create_index("ix_agent_profiles_domain", "agent_profiles", ["domain"])

    # ---------------------------------------------------------- conversations
    op.drop_index("ix_conversations_agent_type", table_name="conversations")
    _rename_keys("conversations", key_nullable=False, domain_nullable=False)
    op.create_index("ix_conversations_agent_key", "conversations", ["agent_key"])
    op.create_index("ix_conversations_domain", "conversations", ["domain"])

    # ---------------------------------------------------------------- messages
    with op.batch_alter_table("messages") as batch:
        batch.alter_column(
            "agent_type",
            new_column_name="agent_key",
            existing_type=sa.String(length=32),
            type_=sa.String(length=80),
            existing_nullable=True,
        )
        batch.add_column(
            sa.Column("output_kind", sa.String(length=16), nullable=False, server_default="text")
        )
        batch.add_column(sa.Column("media", JSONBType, nullable=True))
    for domain, agent_key in DEFAULT_AGENT.items():
        op.execute(
            f"UPDATE messages SET agent_key = '{agent_key}' WHERE agent_key = '{domain}'"
        )
    op.execute("UPDATE messages SET media = '[]' WHERE media IS NULL")
    with op.batch_alter_table("messages") as batch:
        batch.alter_column("media", existing_type=JSONBType, nullable=False)

    # ---------------------------------------------------------------- memories
    op.drop_index("ix_memories_agent_type", table_name="memories")
    op.drop_index("ix_memories_user_agent", table_name="memories")
    _rename_keys("memories", key_nullable=True, domain_nullable=True)
    op.create_index("ix_memories_agent_key", "memories", ["agent_key"])
    op.create_index("ix_memories_domain", "memories", ["domain"])
    op.create_index("ix_memories_user_agent", "memories", ["user_id", "agent_key"])
    op.create_index("ix_memories_user_domain", "memories", ["user_id", "domain"])

    # ---------------------------------------------------------------- feedback
    op.drop_index("ix_feedback_agent_type", table_name="feedback")
    _rename_keys("feedback", key_nullable=False, domain_nullable=False)
    op.create_index("ix_feedback_agent_key", "feedback", ["agent_key"])
    op.create_index("ix_feedback_domain", "feedback", ["domain"])


def _revert_keys(table: str, *, key_nullable: bool) -> None:
    with op.batch_alter_table(table) as batch:
        batch.drop_column("domain")
        batch.alter_column(
            "agent_key",
            new_column_name="agent_type",
            existing_type=sa.String(length=80),
            type_=sa.String(length=32),
            existing_nullable=key_nullable,
        )


def downgrade() -> None:
    # ---------------------------------------------------------------- feedback
    op.drop_index("ix_feedback_domain", table_name="feedback")
    op.drop_index("ix_feedback_agent_key", table_name="feedback")
    _revert_keys("feedback", key_nullable=False)
    op.create_index("ix_feedback_agent_type", "feedback", ["agent_type"])

    # ---------------------------------------------------------------- memories
    op.drop_index("ix_memories_user_domain", table_name="memories")
    op.drop_index("ix_memories_user_agent", table_name="memories")
    op.drop_index("ix_memories_domain", table_name="memories")
    op.drop_index("ix_memories_agent_key", table_name="memories")
    _revert_keys("memories", key_nullable=True)
    op.create_index("ix_memories_agent_type", "memories", ["agent_type"])
    op.create_index("ix_memories_user_agent", "memories", ["user_id", "agent_type"])

    # ---------------------------------------------------------------- messages
    with op.batch_alter_table("messages") as batch:
        batch.drop_column("media")
        batch.drop_column("output_kind")
        batch.alter_column(
            "agent_key",
            new_column_name="agent_type",
            existing_type=sa.String(length=80),
            type_=sa.String(length=32),
            existing_nullable=True,
        )

    # ---------------------------------------------------------- conversations
    op.drop_index("ix_conversations_domain", table_name="conversations")
    op.drop_index("ix_conversations_agent_key", table_name="conversations")
    _revert_keys("conversations", key_nullable=False)
    op.create_index("ix_conversations_agent_type", "conversations", ["agent_type"])

    # --------------------------------------------------------- agent_profiles
    op.drop_index("ix_agent_profiles_domain", table_name="agent_profiles")
    op.drop_index("ix_agent_profiles_agent_key", table_name="agent_profiles")
    with op.batch_alter_table("agent_profiles") as batch:
        batch.drop_column("last_used_at")
    _revert_keys("agent_profiles", key_nullable=False)
    op.create_index("ix_agent_profiles_agent_type", "agent_profiles", ["agent_type"])

    # ------------------------------------------------------- domain_profiles
    op.drop_index("ix_domain_profiles_domain", table_name="domain_profiles")
    op.drop_index("ix_domain_profiles_user_id", table_name="domain_profiles")
    op.drop_table("domain_profiles")
