"""Three levels of personalization profile.

    GlobalProfile  — one per user, applies everywhere
    DomainProfile  — one per (user, domain): board + class, brand + audience, …
    AgentProfile   — one per (user, agent_key): the narrow specifics of one job

An agent's context is assembled from all three, most general first.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.database.types import JSONBType

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User


class GlobalProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Profile information shared by every domain and agent."""

    __tablename__ = "global_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(160), nullable=True)
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    language: Mapped[str] = mapped_column(String(64), default="English", nullable=False)

    # "concise" | "balanced" | "detailed"
    preferred_response_length: Mapped[str] = mapped_column(
        String(32), default="balanced", nullable=False
    )
    # "friendly" | "professional" | "direct" | "casual" | "academic"
    communication_style: Mapped[str] = mapped_column(
        String(32), default="friendly", nullable=False
    )
    general_skill_level: Mapped[str] = mapped_column(
        String(32), default="intermediate", nullable=False
    )

    interests: Mapped[list[str]] = mapped_column(JSONBType, default=list, nullable=False)
    goals: Mapped[list[str]] = mapped_column(JSONBType, default=list, nullable=False)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    personalization_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped[User] = relationship(back_populates="global_profile")

    def to_context_dict(self) -> dict[str, Any]:
        return {
            "display_name": self.display_name,
            "occupation": self.occupation,
            "location": self.location,
            "language": self.language,
            "preferred_response_length": self.preferred_response_length,
            "communication_style": self.communication_style,
            "general_skill_level": self.general_skill_level,
            "interests": list(self.interests or []),
            "goals": list(self.goals or []),
            "preferences": dict(self.preferences or {}),
            "bio": self.bio,
        }


class DomainProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Shared answers for every agent inside one domain."""

    __tablename__ = "domain_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "domain", name="uq_domain_profiles_user_domain"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    #: Catalog domain key, e.g. ``education``.
    domain: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    profile_data: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped[User] = relationship(back_populates="domain_profiles")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DomainProfile {self.domain} user={self.user_id}>"


class AgentProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """The narrow specifics for one agent, e.g. weak chapters for Class 10 Maths."""

    __tablename__ = "agent_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "agent_key", name="uq_agent_profiles_user_agent"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    #: Fully qualified catalog key, e.g. ``education.class10-maths``.
    agent_key: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    #: Denormalised for cheap per-domain queries.
    domain: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    profile_data: Mapped[dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="agent_profiles")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AgentProfile {self.agent_key} user={self.user_id}>"
