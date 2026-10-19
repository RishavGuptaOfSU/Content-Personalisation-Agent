"""Domain and agent catalog routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.agents.catalog import catalog_summary
from app.api.deps import AgentKey, CurrentUser, DbSession, DomainKey
from app.schemas.catalog import (
    AgentDetail,
    AgentSummary,
    CatalogOverview,
    DomainSummary,
)
from app.services.catalog_service import get_catalog_service

router = APIRouter(tags=["catalog"])


@router.get("/domains", response_model=list[DomainSummary])
def list_domains_route(user: CurrentUser, db: DbSession) -> list[DomainSummary]:
    """The dashboard: every domain with this user's counts and setup status."""
    payload = get_catalog_service().domains_for_user(db, user.id)
    return [DomainSummary.model_validate(item) for item in payload]


@router.get("/domains/{domain}/agents", response_model=list[AgentSummary])
def list_domain_agents(domain: DomainKey, user: CurrentUser, db: DbSession) -> list[AgentSummary]:
    """The agents inside one domain — the second level of the dashboard."""
    payload = get_catalog_service().agents_for_user(db, user.id, domain)
    return [AgentSummary.model_validate(item) for item in payload]


@router.get("/agents", response_model=list[AgentSummary])
def list_all_agents(user: CurrentUser, db: DbSession) -> list[AgentSummary]:
    """Every agent across every domain (used by search and the sidebar)."""
    payload = get_catalog_service().agents_for_user(db, user.id)
    return [AgentSummary.model_validate(item) for item in payload]


@router.get("/agents/{agent_key}", response_model=AgentDetail)
def get_agent_detail(agent_key: AgentKey, user: CurrentUser, db: DbSession) -> AgentDetail:
    """One agent: scope, setup forms (domain + agent) and saved answers."""
    payload = get_catalog_service().agent_detail(db, user.id, agent_key)
    return AgentDetail.model_validate(payload)


@router.get("/catalog", response_model=CatalogOverview)
def catalog_overview() -> CatalogOverview:
    """Shape of the catalog. Unauthenticated: it contains no user data."""
    return CatalogOverview.model_validate(catalog_summary())


@router.get("/domains/{domain}", response_model=DomainSummary)
def get_domain_route(domain: DomainKey, user: CurrentUser, db: DbSession) -> DomainSummary:
    payload = get_catalog_service().domains_for_user(db, user.id)
    match = next(item for item in payload if item["key"] == domain)
    return DomainSummary.model_validate(match)
