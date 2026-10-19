"""Global, domain and agent profile schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ResponseLength = Literal["concise", "balanced", "detailed"]
CommunicationStyle = Literal["friendly", "professional", "direct", "casual", "academic"]
SkillLevel = Literal["beginner", "intermediate", "advanced", "expert"]

_MAX_LIST_ITEMS = 40
_MAX_ITEM_LENGTH = 120


def _normalize_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        raise ValueError("Expected a list of strings")
    cleaned: list[str] = []
    for item in value:
        text = str(item).strip()[:_MAX_ITEM_LENGTH]
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:_MAX_LIST_ITEMS]


# --------------------------------------------------------------------- global
class GlobalProfileBase(BaseModel):
    display_name: Annotated[str | None, Field(default=None, max_length=160)] = None
    occupation: Annotated[str | None, Field(default=None, max_length=160)] = None
    location: Annotated[str | None, Field(default=None, max_length=160)] = None
    language: Annotated[str, Field(default="English", max_length=64)] = "English"
    preferred_response_length: ResponseLength = "balanced"
    communication_style: CommunicationStyle = "friendly"
    general_skill_level: SkillLevel = "intermediate"
    interests: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    bio: Annotated[str | None, Field(default=None, max_length=2000)] = None

    @field_validator("interests", "goals", mode="before")
    @classmethod
    def _clean_lists(cls, value: Any) -> list[str]:
        return _normalize_str_list(value)

    @field_validator("preferences", mode="before")
    @classmethod
    def _clean_preferences(cls, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("preferences must be an object")
        if len(value) > 50:
            raise ValueError("Too many preference keys (max 50)")
        return value


class GlobalProfileUpdate(GlobalProfileBase):
    """Full replacement of the mutable global fields."""


class GlobalProfileRead(GlobalProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    personalization_version: int
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------ domain / agent
class ProfileWrite(BaseModel):
    """Answers to a domain or agent setup form.

    Validated against the catalog's declared field keys by the service layer, so
    arbitrary payloads cannot reach the JSONB column.
    """

    profile_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("profile_data", mode="before")
    @classmethod
    def _check_payload(cls, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("profile_data must be an object")
        if len(value) > 60:
            raise ValueError("Too many profile keys (max 60)")
        return value


class DomainProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    domain: str
    profile_data: dict[str, Any]
    is_configured: bool
    revision: int
    created_at: datetime
    updated_at: datetime


class AgentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    agent_key: str
    domain: str
    profile_data: dict[str, Any]
    is_configured: bool
    interaction_count: int
    revision: int
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None = None


class AgentProfileStatus(BaseModel):
    """Drives the setup-vs-chat decision in the UI."""

    agent_key: str
    domain: str
    agent_exists: bool
    agent_configured: bool
    domain_exists: bool
    domain_configured: bool
    needs_setup: bool
    status_label: Literal["Personalized", "Not configured"]
    missing_agent_fields: list[str] = Field(default_factory=list)
    missing_domain_fields: list[str] = Field(default_factory=list)
    agent_profile: AgentProfileRead | None = None
    domain_profile: DomainProfileRead | None = None


class ProfileOverview(BaseModel):
    """Everything the Profile page needs in one call."""

    global_profile: GlobalProfileRead
    domain_profiles: dict[str, DomainProfileRead | None]
    agent_profiles: dict[str, AgentProfileRead | None]
