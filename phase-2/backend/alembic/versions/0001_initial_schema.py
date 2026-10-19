"""Initial schema for the single-domain build.

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-01

This is a fresh, squashed schema. The multi-domain build reached the same shape
through two migrations (an initial schema plus a ``agent_type`` -> ``agent_key``
split); carrying that history into a new application would be archaeology, so
the final shape is created directly here.

Uses the application's own portable column types so the migration produces
``JSONB`` + ``vector(N)`` on PostgreSQL and ``JSON`` on SQLite, matching the ORM
models exactly. ``alembic check`` is the proof of that.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.config import settings
from app.database.types import Embedding, JSONBType

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    is_postgres = op.get_bind().dialect.name == "postgresql"
    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ------------------------------------------------------------------ users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # -------------------------------------------------------- global_profiles
    op.create_table(
        "global_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=True),
        sa.Column("occupation", sa.String(length=160), nullable=True),
        sa.Column("location", sa.String(length=160), nullable=True),
        sa.Column("language", sa.String(length=64), nullable=False, server_default="English"),
        sa.Column(
            "preferred_response_length",
            sa.String(length=32),
            nullable=False,
            server_default="balanced",
        ),
        sa.Column(
            "communication_style", sa.String(length=32), nullable=False, server_default="friendly"
        ),
        sa.Column(
            "general_skill_level",
            sa.String(length=32),
            nullable=False,
            server_default="intermediate",
        ),
        sa.Column("interests", JSONBType, nullable=False),
        sa.Column("goals", JSONBType, nullable=False),
        sa.Column("preferences", JSONBType, nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("personalization_version", sa.Integer(), nullable=False, server_default="1"),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_global_profiles_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_global_profiles"),
    )
    op.create_index("ix_global_profiles_user_id", "global_profiles", ["user_id"], unique=True)

    # -------------------------------------------------------- domain_profiles
    # The brand profile: answered once, reused by every agent in the domain.
    op.create_table(
        "domain_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("profile_data", JSONBType, nullable=False),
        sa.Column("is_configured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_domain_profiles_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_domain_profiles"),
        sa.UniqueConstraint("user_id", "domain", name="uq_domain_profiles_user_domain"),
    )
    op.create_index("ix_domain_profiles_user_id", "domain_profiles", ["user_id"])
    op.create_index("ix_domain_profiles_domain", "domain_profiles", ["domain"])

    # --------------------------------------------------------- agent_profiles
    op.create_table(
        "agent_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("agent_key", sa.String(length=80), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("profile_data", JSONBType, nullable=False),
        sa.Column("is_configured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("interaction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_agent_profiles_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_profiles"),
        sa.UniqueConstraint("user_id", "agent_key", name="uq_agent_profiles_user_agent"),
    )
    op.create_index("ix_agent_profiles_user_id", "agent_profiles", ["user_id"])
    op.create_index("ix_agent_profiles_agent_key", "agent_profiles", ["agent_key"])
    op.create_index("ix_agent_profiles_domain", "agent_profiles", ["domain"])

    # ----------------------------------------------------------- conversations
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("agent_key", sa.String(length=80), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="New conversation"),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("meta", JSONBType, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_conversations_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_conversations"),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_index("ix_conversations_agent_key", "conversations", ["agent_key"])
    op.create_index("ix_conversations_domain", "conversations", ["domain"])

    # ---------------------------------------------------------------- messages
    # output_kind + media are what let one conversation hold prose turns and
    # rendered-image turns side by side.
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("conversation_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("agent_key", sa.String(length=80), nullable=True),
        sa.Column("output_kind", sa.String(length=16), nullable=False, server_default="text"),
        sa.Column("media", JSONBType, nullable=False),
        sa.Column("meta", JSONBType, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name="fk_messages_conversation_id_conversations",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_messages"),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])

    # ---------------------------------------------------------------- memories
    # Scope is agent_key -> domain -> global (both NULL).
    op.create_table(
        "memories",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("agent_key", sa.String(length=80), nullable=True),
        sa.Column("domain", sa.String(length=32), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Embedding(settings.EMBEDDING_DIM), nullable=True),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="preference"),
        sa.Column("importance", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("occurrences", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("meta", JSONBType, nullable=False),
        sa.Column("source_conversation_id", sa.Uuid(as_uuid=True), nullable=True),
        *_timestamps(),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_memories_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["source_conversation_id"],
            ["conversations.id"],
            name="fk_memories_source_conversation_id_conversations",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_memories"),
    )
    op.create_index("ix_memories_user_id", "memories", ["user_id"])
    op.create_index("ix_memories_agent_key", "memories", ["agent_key"])
    op.create_index("ix_memories_domain", "memories", ["domain"])
    op.create_index("ix_memories_user_agent", "memories", ["user_id", "agent_key"])
    op.create_index("ix_memories_user_domain", "memories", ["user_id", "domain"])
    op.create_index("ix_memories_created_at", "memories", ["created_at"])

    if is_postgres:
        # HNSW gives sub-linear cosine search; ivfflat is the pre-0.5 fallback.
        try:
            op.execute(
                "CREATE INDEX IF NOT EXISTS ix_memories_embedding_cosine "
                "ON memories USING hnsw (embedding vector_cosine_ops)"
            )
        except Exception:  # pragma: no cover - depends on the pgvector version
            op.execute(
                "CREATE INDEX IF NOT EXISTS ix_memories_embedding_cosine "
                "ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
            )

    # ---------------------------------------------------------------- feedback
    op.create_table(
        "feedback",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("agent_key", sa.String(length=80), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("message_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("conversation_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("outcome", JSONBType, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_feedback_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["message_id"], ["messages.id"], name="fk_feedback_message_id_messages", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name="fk_feedback_conversation_id_conversations",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_feedback"),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_feedback_agent_key", "feedback", ["agent_key"])
    op.create_index("ix_feedback_domain", "feedback", ["domain"])
    op.create_index("ix_feedback_message_id", "feedback", ["message_id"])
    op.create_index("ix_feedback_created_at", "feedback", ["created_at"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("memories")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("agent_profiles")
    op.drop_table("domain_profiles")
    op.drop_table("global_profiles")
    op.drop_table("users")
