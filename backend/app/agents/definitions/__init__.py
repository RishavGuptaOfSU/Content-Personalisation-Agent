"""Domain definition modules. Add a domain by adding a module and listing it here."""

from app.agents.definitions import (
    analytics,
    career,
    creative,
    education,
    marketing,
    research,
    technical,
)

#: Display order for the dashboard.
DOMAIN_MODULES = (
    education,
    technical,
    career,
    marketing,
    analytics,
    research,
    creative,
)

__all__ = [
    "DOMAIN_MODULES",
    "analytics",
    "career",
    "creative",
    "education",
    "marketing",
    "research",
    "technical",
]
