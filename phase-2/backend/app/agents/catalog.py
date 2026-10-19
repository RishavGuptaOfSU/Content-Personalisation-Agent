"""The domain → agent catalog and its lookup helpers.

Agents are addressed by a **key** of the form ``<domain>.<slug>``, e.g.
``education.class10-maths`` or ``marketing.post-image``. That key is what the
database, API and UI all store and pass around.
"""

from __future__ import annotations

from app.agents.definitions import DOMAIN_MODULES
from app.agents.schema import AgentSpec, DomainSpec, OutputKind

# --------------------------------------------------------------------- build
DOMAINS: dict[str, DomainSpec] = {}
AGENTS: dict[str, AgentSpec] = {}
#: domain key -> agent keys, in declaration order
DOMAIN_AGENTS: dict[str, list[str]] = {}
DOMAIN_ORDER: list[str] = []

for _module in DOMAIN_MODULES:
    _domain: DomainSpec = _module.DOMAIN
    DOMAINS[_domain.key] = _domain
    DOMAIN_ORDER.append(_domain.key)
    DOMAIN_AGENTS[_domain.key] = []
    for _agent in _module.AGENTS:
        if _agent.domain != _domain.key:
            raise ValueError(
                f"Agent {_agent.slug!r} declares domain {_agent.domain!r} "
                f"but lives in the {_domain.key!r} module"
            )
        if _agent.key in AGENTS:
            raise ValueError(f"Duplicate agent key: {_agent.key}")
        AGENTS[_agent.key] = _agent
        DOMAIN_AGENTS[_domain.key].append(_agent.key)


class UnknownAgentError(KeyError):
    """Raised when an agent key does not exist in the catalog."""


class UnknownDomainError(KeyError):
    """Raised when a domain key does not exist in the catalog."""


# -------------------------------------------------------------------- lookup
def get_domain(domain_key: str) -> DomainSpec:
    try:
        return DOMAINS[str(domain_key).strip().lower()]
    except KeyError as exc:
        raise UnknownDomainError(
            f"Unknown domain {domain_key!r}. Valid domains: {', '.join(DOMAIN_ORDER)}"
        ) from exc


def get_agent_spec(agent_key: str) -> AgentSpec:
    key = str(agent_key).strip().lower()
    try:
        return AGENTS[key]
    except KeyError as exc:
        raise UnknownAgentError(f"Unknown agent {agent_key!r}") from exc


def agent_exists(agent_key: str) -> bool:
    return str(agent_key).strip().lower() in AGENTS


def domain_exists(domain_key: str) -> bool:
    return str(domain_key).strip().lower() in DOMAINS


def list_domains() -> list[DomainSpec]:
    return [DOMAINS[key] for key in DOMAIN_ORDER]


def list_agents(domain_key: str | None = None) -> list[AgentSpec]:
    if domain_key is None:
        return [AGENTS[key] for domain in DOMAIN_ORDER for key in DOMAIN_AGENTS[domain]]
    get_domain(domain_key)  # validates
    return [AGENTS[key] for key in DOMAIN_AGENTS[str(domain_key).strip().lower()]]


def agent_keys(domain_key: str | None = None) -> list[str]:
    return [spec.key for spec in list_agents(domain_key)]


def domain_of(agent_key: str) -> str:
    return get_agent_spec(agent_key).domain


def image_agents() -> list[AgentSpec]:
    """Agents whose deliverable is a rendered image or chart."""
    return [spec for spec in list_agents() if spec.output_kind.is_visual]


def default_agent_for(domain_key: str) -> AgentSpec:
    """The first agent in a domain — used when only a domain is known."""
    agents = list_agents(domain_key)
    if not agents:
        raise UnknownDomainError(f"Domain {domain_key!r} has no agents")
    return agents[0]


def catalog_summary() -> dict[str, object]:
    """Small payload used by ``/health`` and the docs."""
    return {
        "domains": len(DOMAINS),
        "agents": len(AGENTS),
        "by_domain": {key: len(DOMAIN_AGENTS[key]) for key in DOMAIN_ORDER},
        "image_agents": [spec.key for spec in image_agents()],
        "output_kinds": {kind.value: sum(
            1 for spec in list_agents() if spec.output_kind is kind
        ) for kind in OutputKind},
    }


__all__ = [
    "AGENTS",
    "DOMAINS",
    "DOMAIN_AGENTS",
    "DOMAIN_ORDER",
    "AgentSpec",
    "DomainSpec",
    "OutputKind",
    "UnknownAgentError",
    "UnknownDomainError",
    "agent_exists",
    "agent_keys",
    "catalog_summary",
    "default_agent_for",
    "domain_exists",
    "domain_of",
    "get_agent_spec",
    "get_domain",
    "image_agents",
    "list_agents",
    "list_domains",
]
