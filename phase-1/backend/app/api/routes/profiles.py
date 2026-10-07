"""Global, domain and agent profile routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.agents.catalog import DOMAIN_ORDER, agent_keys
from app.api.deps import AgentKey, CurrentUser, DbSession, DomainKey
from app.schemas.profile import (
    AgentProfileRead,
    AgentProfileStatus,
    DomainProfileRead,
    GlobalProfileRead,
    GlobalProfileUpdate,
    ProfileOverview,
    ProfileWrite,
)
from app.services.profile_service import get_profile_service

router = APIRouter(prefix="/profile", tags=["profiles"])


# --------------------------------------------------------------------- global
@router.get("/global", response_model=GlobalProfileRead)
def read_global_profile(user: CurrentUser, db: DbSession) -> GlobalProfileRead:
    profile = get_profile_service().get_or_create_global_profile(db, user)
    return GlobalProfileRead.model_validate(profile)


@router.put("/global", response_model=GlobalProfileRead)
def update_global_profile(
    payload: GlobalProfileUpdate, user: CurrentUser, db: DbSession
) -> GlobalProfileRead:
    profile = get_profile_service().update_global_profile(db, user, payload.model_dump())
    return GlobalProfileRead.model_validate(profile)


@router.get("/overview", response_model=ProfileOverview)
def profile_overview(user: CurrentUser, db: DbSession) -> ProfileOverview:
    """Global + every domain + every agent profile, for the Profile page."""
    service = get_profile_service()
    global_profile = service.get_or_create_global_profile(db, user)
    domain_profiles = service.list_domain_profiles(db, user.id)
    agent_profiles = service.list_agent_profiles(db, user.id)

    return ProfileOverview(
        global_profile=GlobalProfileRead.model_validate(global_profile),
        domain_profiles={
            key: (
                DomainProfileRead.model_validate(domain_profiles[key])
                if key in domain_profiles
                else None
            )
            for key in DOMAIN_ORDER
        },
        agent_profiles={
            key: (
                AgentProfileRead.model_validate(agent_profiles[key])
                if key in agent_profiles
                else None
            )
            for key in agent_keys()
        },
    )


# --------------------------------------------------------------------- domain
@router.get("/domain/{domain}", response_model=DomainProfileRead | None)
def read_domain_profile(
    domain: DomainKey, user: CurrentUser, db: DbSession
) -> DomainProfileRead | None:
    profile = get_profile_service().get_domain_profile(db, user.id, domain)
    return DomainProfileRead.model_validate(profile) if profile else None


@router.put("/domain/{domain}", response_model=DomainProfileRead)
def save_domain_profile(
    domain: DomainKey, payload: ProfileWrite, user: CurrentUser, db: DbSession
) -> DomainProfileRead:
    """Create or update the profile shared by every agent in this domain."""
    profile = get_profile_service().save_domain_profile(
        db, user.id, domain, payload.profile_data
    )
    return DomainProfileRead.model_validate(profile)


# ---------------------------------------------------------------------- agent
@router.get("/agent/{agent_key}", response_model=AgentProfileStatus)
def read_agent_profile(
    agent_key: AgentKey, user: CurrentUser, db: DbSession
) -> AgentProfileStatus:
    """Status for one agent — the UI uses ``needs_setup`` to route to setup."""
    service = get_profile_service()
    status = service.agent_status(db, user.id, agent_key)
    agent_profile = service.get_agent_profile(db, user.id, agent_key)
    domain_profile = service.get_domain_profile(db, user.id, status["domain"])
    return AgentProfileStatus(
        **status,
        agent_profile=AgentProfileRead.model_validate(agent_profile) if agent_profile else None,
        domain_profile=(
            DomainProfileRead.model_validate(domain_profile) if domain_profile else None
        ),
    )


@router.put("/agent/{agent_key}", response_model=AgentProfileRead)
def save_agent_profile(
    agent_key: AgentKey, payload: ProfileWrite, user: CurrentUser, db: DbSession
) -> AgentProfileRead:
    """Create or replace this agent's own profile."""
    profile = get_profile_service().save_agent_profile(
        db, user.id, agent_key, payload.profile_data
    )
    return AgentProfileRead.model_validate(profile)


@router.patch("/agent/{agent_key}", response_model=AgentProfileRead)
def patch_agent_profile(
    agent_key: AgentKey, payload: ProfileWrite, user: CurrentUser, db: DbSession
) -> AgentProfileRead:
    """Merge only the supplied keys into this agent's profile."""
    profile = get_profile_service().save_agent_profile(
        db, user.id, agent_key, payload.profile_data, merge=True
    )
    return AgentProfileRead.model_validate(profile)
