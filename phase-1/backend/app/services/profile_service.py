"""Global, domain and agent profile management."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.catalog import get_agent_spec, get_domain
from app.core.logging import get_logger
from app.models.profiles import AgentProfile, DomainProfile, GlobalProfile
from app.models.user import User

logger = get_logger(__name__)

_ALLOWED_GLOBAL_FIELDS = {
    "display_name",
    "occupation",
    "location",
    "language",
    "preferred_response_length",
    "communication_style",
    "general_skill_level",
    "interests",
    "goals",
    "preferences",
    "bio",
}

_HISTORY_KEY = "history"


class ProfileService:
    # ------------------------------------------------------------- global
    def get_or_create_global_profile(self, db: Session, user: User) -> GlobalProfile:
        profile = db.scalar(select(GlobalProfile).where(GlobalProfile.user_id == user.id))
        if profile is None:
            profile = GlobalProfile(
                user_id=user.id,
                display_name=user.name,
                interests=[],
                goals=[],
                preferences={},
                personalization_version=1,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            logger.info("Created global profile for %s", user.id)
        return profile

    def update_global_profile(
        self, db: Session, user: User, payload: dict[str, Any]
    ) -> GlobalProfile:
        profile = self.get_or_create_global_profile(db, user)
        for key, value in payload.items():
            if key in _ALLOWED_GLOBAL_FIELDS:
                setattr(profile, key, value)
        profile.personalization_version = (profile.personalization_version or 1) + 1
        db.commit()
        db.refresh(profile)
        return profile

    def apply_learned_global_preference(
        self, db: Session, user_id: uuid.UUID, key: str, value: Any
    ) -> bool:
        profile = db.scalar(select(GlobalProfile).where(GlobalProfile.user_id == user_id))
        if profile is None or key not in _ALLOWED_GLOBAL_FIELDS:
            return False
        if getattr(profile, key, None) == value:
            return False
        setattr(profile, key, value)
        profile.personalization_version = (profile.personalization_version or 1) + 1
        db.flush()
        logger.info("Global profile adapted: %s -> %r", key, value)
        return True

    # ------------------------------------------------------------- domain
    def get_domain_profile(
        self, db: Session, user_id: uuid.UUID, domain_key: str
    ) -> DomainProfile | None:
        spec = get_domain(domain_key)
        return db.scalar(
            select(DomainProfile).where(
                DomainProfile.user_id == user_id, DomainProfile.domain == spec.key
            )
        )

    def list_domain_profiles(self, db: Session, user_id: uuid.UUID) -> dict[str, DomainProfile]:
        rows = db.scalars(select(DomainProfile).where(DomainProfile.user_id == user_id)).all()
        return {row.domain: row for row in rows}

    def save_domain_profile(
        self, db: Session, user_id: uuid.UUID, domain_key: str, profile_data: dict[str, Any]
    ) -> DomainProfile:
        spec = get_domain(domain_key)
        cleaned = self._sanitize(spec.profile_fields, profile_data)

        profile = self.get_domain_profile(db, user_id, spec.key)
        if profile is None:
            profile = DomainProfile(
                user_id=user_id, domain=spec.key, profile_data=cleaned, revision=1
            )
            db.add(profile)
        else:
            merged = dict(profile.profile_data or {})
            merged.update(cleaned)
            profile.profile_data = merged
            profile.revision = (profile.revision or 1) + 1

        profile.is_configured = self._is_configured(spec.profile_fields, profile.profile_data)
        db.commit()
        db.refresh(profile)
        logger.info("Saved %s domain profile (configured=%s)", spec.key, profile.is_configured)
        return profile

    # -------------------------------------------------------------- agent
    def get_agent_profile(
        self, db: Session, user_id: uuid.UUID, agent_key: str
    ) -> AgentProfile | None:
        spec = get_agent_spec(agent_key)
        return db.scalar(
            select(AgentProfile).where(
                AgentProfile.user_id == user_id, AgentProfile.agent_key == spec.key
            )
        )

    def list_agent_profiles(self, db: Session, user_id: uuid.UUID) -> dict[str, AgentProfile]:
        rows = db.scalars(select(AgentProfile).where(AgentProfile.user_id == user_id)).all()
        return {row.agent_key: row for row in rows}

    def save_agent_profile(
        self,
        db: Session,
        user_id: uuid.UUID,
        agent_key: str,
        profile_data: dict[str, Any],
        *,
        merge: bool = False,
    ) -> AgentProfile:
        spec = get_agent_spec(agent_key)
        cleaned = self._sanitize(spec.profile_fields, profile_data)

        profile = self.get_agent_profile(db, user_id, spec.key)
        if profile is None:
            cleaned.setdefault(_HISTORY_KEY, [])
            profile = AgentProfile(
                user_id=user_id,
                agent_key=spec.key,
                domain=spec.domain,
                profile_data=cleaned,
                interaction_count=0,
                revision=1,
            )
            db.add(profile)
        else:
            data = dict(profile.profile_data or {}) if merge else {}
            data.update(cleaned)
            data.setdefault(_HISTORY_KEY, (profile.profile_data or {}).get(_HISTORY_KEY, []))
            profile.profile_data = data
            profile.revision = (profile.revision or 1) + 1

        profile.is_configured = self._is_configured(spec.profile_fields, profile.profile_data)
        db.commit()
        db.refresh(profile)
        logger.info("Saved %s profile (configured=%s)", spec.key, profile.is_configured)
        return profile

    def ensure_agent_profile(
        self, db: Session, user_id: uuid.UUID, agent_key: str
    ) -> AgentProfile:
        """Return the profile, creating an unconfigured placeholder if needed, so a
        conversation can start before setup is completed."""
        profile = self.get_agent_profile(db, user_id, agent_key)
        if profile is not None:
            return profile
        spec = get_agent_spec(agent_key)
        profile = AgentProfile(
            user_id=user_id,
            agent_key=spec.key,
            domain=spec.domain,
            profile_data=spec.default_profile(),
            is_configured=False,
            interaction_count=0,
            revision=1,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def record_interaction(
        self, db: Session, profile: AgentProfile, topic: str | None = None
    ) -> None:
        profile.interaction_count = (profile.interaction_count or 0) + 1
        profile.last_used_at = datetime.now(UTC)
        if topic:
            data = dict(profile.profile_data or {})
            history = list(data.get(_HISTORY_KEY) or [])
            entry = topic.strip()[:120]
            if entry and (not history or history[-1] != entry):
                history.append(entry)
            data[_HISTORY_KEY] = history[-20:]
            profile.profile_data = data
        db.flush()

    def apply_learned_agent_preference(
        self, db: Session, profile: AgentProfile, key: str, value: Any
    ) -> bool:
        spec = get_agent_spec(profile.agent_key)
        if key not in {field.key for field in spec.profile_fields}:
            return False
        data = dict(profile.profile_data or {})
        if data.get(key) == value:
            return False
        data[key] = value
        profile.profile_data = data
        profile.revision = (profile.revision or 1) + 1
        db.flush()
        logger.info("Agent profile adapted: %s.%s -> %r", profile.agent_key, key, value)
        return True

    # ------------------------------------------------------------- status
    def missing_required(
        self, fields: tuple, profile_data: dict[str, Any] | None
    ) -> list[str]:
        data = profile_data or {}
        return [
            field.key
            for field in fields
            if field.required and data.get(field.key) in (None, "", [], {})
        ]

    def agent_status(
        self, db: Session, user_id: uuid.UUID, agent_key: str
    ) -> dict[str, Any]:
        """Everything the UI needs to decide setup-vs-chat for one agent."""
        spec = get_agent_spec(agent_key)
        domain = get_domain(spec.domain)
        agent_profile = self.get_agent_profile(db, user_id, spec.key)
        domain_profile = self.get_domain_profile(db, user_id, spec.domain)

        agent_data = agent_profile.profile_data if agent_profile else None
        domain_data = domain_profile.profile_data if domain_profile else None
        agent_missing = self.missing_required(spec.profile_fields, agent_data)
        domain_missing = self.missing_required(domain.profile_fields, domain_data)

        agent_ok = bool(agent_profile and agent_profile.is_configured)
        domain_ok = bool(domain_profile and domain_profile.is_configured)
        return {
            "agent_key": spec.key,
            "domain": spec.domain,
            "agent_exists": agent_profile is not None,
            "agent_configured": agent_ok,
            "domain_exists": domain_profile is not None,
            "domain_configured": domain_ok,
            "needs_setup": not (agent_ok and domain_ok),
            "missing_agent_fields": agent_missing,
            "missing_domain_fields": domain_missing,
            "status_label": "Personalized" if agent_ok and domain_ok else "Not configured",
        }

    # ---------------------------------------------------------- internals
    def _sanitize(self, fields: tuple, payload: dict[str, Any]) -> dict[str, Any]:
        """Drop unknown keys and coerce values to the declared field kind."""
        allowed = {field.key: field for field in fields}
        cleaned: dict[str, Any] = {}
        for key, value in (payload or {}).items():
            if key == _HISTORY_KEY:
                if isinstance(value, list):
                    cleaned[key] = [str(item)[:160] for item in value][-20:]
                continue
            field = allowed.get(key)
            if field is None:
                continue
            cleaned[key] = self._coerce(field, value)
        return cleaned

    @staticmethod
    def _coerce(field: Any, value: Any) -> Any:
        if field.kind in ("multiselect", "tags"):
            if value is None:
                return []
            if isinstance(value, str):
                items = [part.strip() for part in value.split(",")]
            elif isinstance(value, (list, tuple, set)):
                items = [str(item).strip() for item in value]
            else:
                items = [str(value).strip()]
            unique: list[str] = []
            for item in items:
                if item and item not in unique:
                    unique.append(item[:120])
            return unique[:30]
        if field.kind == "number":
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        if value is None:
            return ""
        text = str(value).strip()
        return text[: 4000 if field.kind == "textarea" else 400]

    @staticmethod
    def _is_configured(fields: tuple, data: dict[str, Any]) -> bool:
        required = [field.key for field in fields if field.required]
        if required:
            return all(data.get(key) not in (None, "", [], {}) for key in required)
        return any(
            value not in (None, "", [], {})
            for key, value in (data or {}).items()
            if key != _HISTORY_KEY
        )


_service: ProfileService | None = None


def get_profile_service() -> ProfileService:
    global _service
    if _service is None:
        _service = ProfileService()
    return _service
