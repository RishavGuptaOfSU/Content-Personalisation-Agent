"""Core structures for the domain → agent catalog.

The platform is organised in two levels:

    DOMAIN  (education, technical, marketing, …)
      └── AGENT  (education.class10-maths, marketing.post-image, …)

A **domain** is a subject area. An **agent** is a single narrow job inside that
domain — "Class 10 Maths tutor", "Social post image generator" — and it answers
*only* requests belonging to that job. Anything else is redirected to the agent
that owns it.

Each agent also declares what it *produces* (``OutputKind``). A post generator
returns an image; a tutor returns text; a chart builder returns a rendered chart.
This module carries no heavy imports so the ORM, API and agent runtime can all
share it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

FieldKind = Literal["text", "textarea", "select", "multiselect", "tags", "number"]


class OutputKind(str, Enum):
    """What an agent hands back to the user."""

    TEXT = "text"
    #: A generated image (social post, poster, ad creative).
    IMAGE = "image"
    #: A rendered data chart produced from supplied data.
    CHART = "chart"

    @property
    def is_visual(self) -> bool:
        return self in (OutputKind.IMAGE, OutputKind.CHART)


@dataclass(frozen=True, slots=True)
class ProfileField:
    """One question in an agent's or domain's profile setup form."""

    key: str
    label: str
    kind: FieldKind
    options: tuple[str, ...] = ()
    placeholder: str = ""
    help_text: str = ""
    required: bool = False
    default: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "kind": self.kind,
            "options": list(self.options),
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            "required": self.required,
            "default": self.default,
        }


@dataclass(frozen=True, slots=True)
class DomainSpec:
    """A subject area that groups related agents."""

    key: str
    name: str
    tagline: str
    description: str
    icon: str  # lucide-react icon name
    accent: str
    #: Profile questions shared by every agent in the domain (e.g. board + class
    #: for education). Answered once, reused by all of the domain's agents.
    profile_fields: tuple[ProfileField, ...] = ()
    setup_headline: str = ""

    def default_profile(self) -> dict[str, Any]:
        return _defaults_for(self.profile_fields)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "icon": self.icon,
            "accent": self.accent,
            "setup_headline": self.setup_headline,
            "profile_fields": [f.to_dict() for f in self.profile_fields],
        }


@dataclass(frozen=True, slots=True)
class AgentSpec:
    """A single-purpose agent inside a domain."""

    #: Short id, unique within the domain (e.g. ``class10-maths``).
    slug: str
    domain: str
    name: str
    tagline: str
    description: str
    icon: str
    output_kind: OutputKind

    #: One sentence stating exactly what this agent does. Injected into the
    #: prompt and used by the scope guard.
    scope: str
    #: Things this agent must refuse and hand off instead of attempting.
    out_of_scope: tuple[str, ...]
    #: Task instructions for the model.
    instructions: str

    #: Example in-scope requests. Shown in the UI and used for routing.
    examples: tuple[str, ...] = ()
    #: Routing/scope vocabulary. Multi-word phrases score higher.
    keywords: tuple[str, ...] = ()
    #: Agent-specific setup questions (narrow — the domain holds shared ones).
    profile_fields: tuple[ProfileField, ...] = ()
    setup_headline: str = ""
    #: Extra knobs for image/chart agents (sizes, styles…).
    options: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        """Globally unique agent key, e.g. ``marketing.post-image``."""
        return f"{self.domain}.{self.slug}"

    @property
    def history_key(self) -> str:
        return "history"

    def default_profile(self) -> dict[str, Any]:
        defaults = _defaults_for(self.profile_fields)
        defaults[self.history_key] = []
        return defaults

    def required_keys(self) -> list[str]:
        return [f.key for f in self.profile_fields if f.required]

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "slug": self.slug,
            "domain": self.domain,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "icon": self.icon,
            "output_kind": self.output_kind.value,
            "scope": self.scope,
            "out_of_scope": list(self.out_of_scope),
            "examples": list(self.examples),
            "setup_headline": self.setup_headline
            or f"Personalize your {self.name}",
            "profile_fields": [f.to_dict() for f in self.profile_fields],
            "history_key": self.history_key,
            "options": dict(self.options),
        }


def _defaults_for(fields: tuple[ProfileField, ...]) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for profile_field in fields:
        if profile_field.default is not None:
            defaults[profile_field.key] = profile_field.default
        elif profile_field.kind in ("multiselect", "tags"):
            defaults[profile_field.key] = []
        else:
            defaults[profile_field.key] = ""
    return defaults


__all__ = ["AgentSpec", "DomainSpec", "FieldKind", "OutputKind", "ProfileField"]
