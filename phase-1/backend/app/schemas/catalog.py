"""Domain and agent catalog schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

OutputKindLiteral = Literal["text", "image", "chart"]
StatusLabel = Literal["Personalized", "Not configured"]


class ProfileFieldSchema(BaseModel):
    key: str
    label: str
    kind: Literal["text", "textarea", "select", "multiselect", "tags", "number"]
    options: list[str] = Field(default_factory=list)
    placeholder: str = ""
    help_text: str = ""
    required: bool = False
    default: Any = None


class DomainSummary(BaseModel):
    """A domain card on the dashboard."""

    key: str
    name: str
    tagline: str
    description: str
    icon: str
    accent: str
    agent_count: int
    configured_agents: int
    conversation_count: int
    message_count: int
    memory_count: int
    domain_profile_configured: bool
    status_label: StatusLabel
    last_used_at: str | None = None
    visual_agents: list[str] = Field(default_factory=list)
    setup_headline: str = ""
    profile_fields: list[ProfileFieldSchema] = Field(default_factory=list)


class AgentSummary(BaseModel):
    """An agent card inside a domain."""

    key: str
    slug: str
    domain: str
    name: str
    tagline: str
    description: str
    icon: str
    output_kind: OutputKindLiteral
    scope: str
    examples: list[str] = Field(default_factory=list)
    conversation_count: int = 0
    message_count: int = 0
    memory_count: int = 0
    is_configured: bool = False
    status_label: StatusLabel = "Not configured"
    last_used_at: str | None = None


class AgentDetail(AgentSummary):
    """Everything the chat screen and setup form need for one agent."""

    out_of_scope: list[str] = Field(default_factory=list)
    setup_headline: str = ""
    profile_fields: list[ProfileFieldSchema] = Field(default_factory=list)
    profile_data: dict[str, Any] | None = None
    history_key: str = "history"
    options: dict[str, Any] = Field(default_factory=dict)

    domain_name: str
    domain_accent: str
    domain_icon: str
    domain_setup_headline: str = ""
    domain_profile_fields: list[ProfileFieldSchema] = Field(default_factory=list)
    domain_profile_data: dict[str, Any] | None = None

    agent_exists: bool = False
    agent_configured: bool = False
    domain_exists: bool = False
    domain_configured: bool = False
    needs_setup: bool = True
    missing_agent_fields: list[str] = Field(default_factory=list)
    missing_domain_fields: list[str] = Field(default_factory=list)


class CatalogOverview(BaseModel):
    domains: int
    agents: int
    by_domain: dict[str, int] = Field(default_factory=dict)
    image_agents: list[str] = Field(default_factory=list)
    output_kinds: dict[str, int] = Field(default_factory=dict)
