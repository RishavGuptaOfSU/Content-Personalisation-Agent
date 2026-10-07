"""Personalization engine.

Assembles, for every request, in order of increasing specificity:

  1. the **global** profile      — tone, length, skill level, language
  2. the **domain** profile      — board + class, brand + audience, warehouse…
  3. the **agent** profile       — the narrow specifics of this one job
  4. relevant **short-term** conversation history
  5. relevant **long-term** memories (agent → domain → global scope)
  6. the current request, plus any attachment

The assembled trace is returned to the client so the UI can show exactly which
signals shaped the answer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.catalog import AgentSpec, get_agent_spec, get_domain
from app.core.config import settings
from app.core.logging import get_logger
from app.core.request_hints import detect_request_constraints
from app.llm.base import ChatMessage
from app.memory.service import get_memory_service
from app.memory.vector_store import ScoredMemory
from app.models.conversation import Message
from app.models.profiles import AgentProfile, DomainProfile, GlobalProfile
from app.models.user import User

logger = get_logger(__name__)

_LENGTH_INSTRUCTION = {
    "concise": (
        "Answer in under 180 words. No preamble, no restating the question."
    ),
    "balanced": "Aim for 200-350 words. Cover the essentials without padding.",
    "detailed": (
        "Go deep: 450-700 words, with structure, edge cases and a worked example."
    ),
}

_STYLE_INSTRUCTION = {
    "friendly": "Warm and plain-spoken. Second person. No corporate filler.",
    "professional": "Precise and neutral. No slang, no exclamation marks.",
    "direct": "Blunt and compressed. Lead with the answer. Cut every hedge.",
    "casual": "Conversational and relaxed. Contractions are fine.",
    "academic": "Formal register, define terms, note limitations explicitly.",
}

_SKILL_INSTRUCTION = {
    "beginner": "Assume no background. Define jargon on first use.",
    "intermediate": "Assume working familiarity. Skip the basics.",
    "advanced": "Assume strong background. Go straight to the non-obvious parts.",
    "expert": "Peer-level. Prioritise trade-offs and failure modes.",
}


@dataclass(slots=True)
class PersonalizedContext:
    agent_key: str
    agent_spec: AgentSpec
    system_prompt: str
    context_block: str
    short_term: list[ChatMessage]
    memories: list[ScoredMemory]
    hints: dict[str, Any]
    global_summary: list[str] = field(default_factory=list)
    domain_summary: list[str] = field(default_factory=list)
    agent_summary: list[str] = field(default_factory=list)
    user_request: str = ""

    @property
    def domain(self) -> str:
        return self.agent_spec.domain

    def to_messages(self) -> list[ChatMessage]:
        messages: list[ChatMessage] = []
        if self.context_block:
            messages.append(
                ChatMessage(
                    role="user",
                    content=(
                        "Personalization context for this conversation. Do not repeat "
                        "it back.\n\n" + self.context_block
                    ),
                )
            )
            messages.append(
                ChatMessage(role="assistant", content="Understood. I'll apply that.")
            )
        messages.extend(self.short_term)
        messages.append(ChatMessage(role="user", content=self.user_request))
        return messages

    @property
    def context_characters(self) -> int:
        return (
            len(self.system_prompt)
            + len(self.context_block)
            + sum(len(message.content) for message in self.short_term)
        )


class PersonalizationEngine:
    def __init__(self) -> None:
        self._memory = get_memory_service()

    # ------------------------------------------------------------------ api
    def build(
        self,
        db: Session,
        *,
        user: User,
        agent_key: str,
        request: str,
        global_profile: GlobalProfile,
        domain_profile: DomainProfile | None,
        agent_profile: AgentProfile | None,
        conversation_id: uuid.UUID | None,
        attachment_name: str | None = None,
        attachment_text: str | None = None,
        memories: list[ScoredMemory] | None = None,
    ) -> PersonalizedContext:
        spec = get_agent_spec(agent_key)
        domain = get_domain(spec.domain)

        global_data = global_profile.to_context_dict()
        domain_data: dict[str, Any] = dict((domain_profile.profile_data if domain_profile else {}) or {})
        agent_data: dict[str, Any] = dict((agent_profile.profile_data if agent_profile else {}) or {})

        constraints = detect_request_constraints(request)
        trivial = constraints["trivial"]

        if memories is None:
            memories = [] if trivial else self.retrieve_memories(
                db, user_id=user.id, agent_key=spec.key, request=request
            )

        history_budget = (
            settings.SHORT_TERM_TRIVIAL_MAX_CHARS if trivial else settings.SHORT_TERM_MAX_CHARS
        )
        short_term = self._load_short_term(db, conversation_id, max_chars=history_budget)

        if trivial:
            global_summary = [
                f"Name: {global_data.get('display_name') or user.name}",
                f"Communication style: {global_data.get('communication_style')}",
            ]
            domain_summary: list[str] = []
            agent_summary: list[str] = []
            memories = []
        else:
            global_summary = self._summarize_global(global_data, user)
            domain_summary = self._summarize_fields(domain.profile_fields, domain_data)
            agent_summary = self._summarize_fields(spec.profile_fields, agent_data)

        context_block = self._render_context_block(
            spec=spec,
            domain_name=domain.name,
            global_summary=global_summary,
            domain_summary=domain_summary,
            agent_summary=agent_summary,
            memories=memories,
            trivial=trivial,
            attachment_name=attachment_name,
            attachment_text=attachment_text,
        )

        user_request = request
        if attachment_text:
            user_request = (
                f"{request}\n\n--- Attached file: {attachment_name or 'attachment'} ---\n"
                f"{attachment_text[:20000]}\n--- end of attachment ---"
            )

        hints = {
            "task": "chat",
            "agent_key": spec.key,
            "agent_name": spec.name,
            "domain": spec.domain,
            "output_kind": spec.output_kind.value,
            "request": request,
            "global_profile": global_data,
            "domain_profile": domain_data,
            "agent_profile": agent_data,
            "memories": [scored.memory.content for scored in memories],
            "recent_turns": len(short_term),
            "attachment": (
                {"name": attachment_name, "chars": len(attachment_text or "")}
                if attachment_text
                else None
            ),
        }

        return PersonalizedContext(
            agent_key=spec.key,
            agent_spec=spec,
            system_prompt=self._render_output_contract(global_data),
            context_block=context_block,
            short_term=short_term,
            memories=memories,
            hints=hints,
            global_summary=global_summary,
            domain_summary=domain_summary,
            agent_summary=agent_summary,
            user_request=user_request,
        )

    def retrieve_memories(
        self, db: Session, *, user_id: uuid.UUID, agent_key: str, request: str
    ) -> list[ScoredMemory]:
        """Step 5, exposed as its own LangGraph node."""
        spec = get_agent_spec(agent_key)
        return self._memory.retrieve(
            db,
            user_id=user_id,
            query=request,
            agent_key=spec.key,
            domain=spec.domain,
        )

    # -------------------------------------------------------------- helpers
    @staticmethod
    def _condense(content: str, limit: int) -> str:
        text = content or ""
        if len(text) <= limit:
            return text
        head = int(limit * 0.6)
        tail = limit - head
        return (
            f"{text[:head].rstrip()}\n\n[… {len(text) - limit} characters trimmed …]\n\n"
            f"{text[-tail:].lstrip()}"
        )

    @classmethod
    def _load_short_term(
        cls, db: Session, conversation_id: uuid.UUID | None, max_chars: int | None = None
    ) -> list[ChatMessage]:
        """Recent turns, bounded by count *and* characters (prompt-eval cost)."""
        if conversation_id is None:
            return []
        rows = db.scalars(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.role.in_(("user", "assistant")),
            )
            .order_by(Message.created_at.desc())
            .limit(settings.SHORT_TERM_WINDOW)
        ).all()

        budget = settings.SHORT_TERM_MAX_CHARS if max_chars is None else max_chars
        per_message = settings.SHORT_TERM_MESSAGE_MAX_CHARS
        selected: list[ChatMessage] = []

        for row in rows:  # newest first
            content = cls._condense(row.content, per_message)
            if selected and len(content) > budget:
                break
            budget -= len(content)
            selected.append(
                ChatMessage(
                    role="assistant" if row.role == "assistant" else "user", content=content
                )
            )
            if budget <= 0:
                break
        return list(reversed(selected))

    @staticmethod
    def _summarize_global(global_data: dict[str, Any], user: User) -> list[str]:
        lines = [f"Name: {global_data.get('display_name') or user.name}"]
        for key, label in (
            ("occupation", "Occupation"),
            ("location", "Location"),
        ):
            if global_data.get(key):
                lines.append(f"{label}: {global_data[key]}")
        lines.append(f"Preferred response length: {global_data.get('preferred_response_length')}")
        lines.append(f"Communication style: {global_data.get('communication_style')}")
        lines.append(f"General skill level: {global_data.get('general_skill_level')}")
        if global_data.get("language") and global_data["language"] != "English":
            lines.append(f"Preferred language: {global_data['language']}")
        if global_data.get("interests"):
            lines.append("Interests: " + ", ".join(global_data["interests"][:8]))
        if global_data.get("bio"):
            lines.append(f"About: {str(global_data['bio'])[:300]}")
        return lines

    @staticmethod
    def _summarize_fields(fields: tuple, data: dict[str, Any]) -> list[str]:
        """Render only the answered fields of a profile, using their labels."""
        lines: list[str] = []
        for profile_field in fields:
            value = data.get(profile_field.key)
            if value in (None, "", [], {}):
                continue
            rendered = (
                ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
            )
            lines.append(f"{profile_field.label}: {rendered[:400]}")
        history = data.get("history") or []
        if history:
            lines.append(f"Recent requests here: {', '.join(str(i) for i in history[-4:])}")
        return lines

    @staticmethod
    def _render_context_block(
        *,
        spec: AgentSpec,
        domain_name: str,
        global_summary: list[str],
        domain_summary: list[str],
        agent_summary: list[str],
        memories: list[ScoredMemory],
        trivial: bool,
        attachment_name: str | None,
        attachment_text: str | None,
    ) -> str:
        sections = ["=== PERSONALIZATION CONTEXT ==="]
        sections.append("\n[GLOBAL PROFILE]")
        sections.append("\n".join(f"- {line}" for line in global_summary) or "- (empty)")

        if trivial:
            sections.append(
                "\n[NOTE] This turn is a greeting, not a task. No task context is "
                "provided on purpose — do not continue or re-answer an earlier topic."
            )
            sections.append("\n=== END CONTEXT ===")
            return "\n".join(sections)

        sections.append(f"\n[{domain_name.upper()} DOMAIN PROFILE — shared by this domain]")
        sections.append(
            "\n".join(f"- {line}" for line in domain_summary)
            or "- Not set up yet. Ask at most one short clarifying question if essential."
        )

        sections.append(f"\n[{spec.name.upper()} PROFILE — this agent only]")
        sections.append(
            "\n".join(f"- {line}" for line in agent_summary)
            or "- Not set up yet; rely on the domain profile."
        )

        if memories:
            sections.append("\n[LEARNED MEMORIES]")
            sections.append(
                "Items marked STANDING are instructions the user has repeated — they "
                "override the defaults above. Apply all of them silently."
            )
            for scored in memories:
                marker = "STANDING" if scored.pinned else "recalled"
                scope = scored.memory.agent_key or scored.memory.domain or "global"
                sections.append(
                    f"- [{marker}] {scored.memory.content} "
                    f"(scope={scope}, seen {scored.memory.occurrences}x, "
                    f"relevance={scored.similarity:.2f})"
                )

        if attachment_text:
            sections.append("\n[ATTACHMENT]")
            sections.append(
                f"- `{attachment_name or 'file'}` ({len(attachment_text)} characters) is "
                f"included with the request below."
            )

        sections.append("\n=== END CONTEXT ===")
        return "\n".join(sections)

    @staticmethod
    def _render_output_contract(global_data: dict[str, Any]) -> str:
        length_key = str(global_data.get("preferred_response_length") or "balanced")
        style_key = str(global_data.get("communication_style") or "friendly")
        skill_key = str(global_data.get("general_skill_level") or "intermediate")

        directives = [
            _LENGTH_INSTRUCTION.get(length_key, _LENGTH_INSTRUCTION["balanced"]),
            _STYLE_INSTRUCTION.get(style_key, _STYLE_INSTRUCTION["friendly"]),
            _SKILL_INSTRUCTION.get(skill_key, _SKILL_INSTRUCTION["intermediate"]),
        ]
        language = str(global_data.get("language") or "English")
        if language.lower() != "english":
            directives.append(f"Reply in {language}.")

        return (
            "=== USER OUTPUT CONTRACT ===\n"
            + "\n".join(f"- {directive}" for directive in directives)
            + "\n- Never claim to know something about the user that is not stated above."
        )


_engine: PersonalizationEngine | None = None


def get_personalization_engine() -> PersonalizationEngine:
    global _engine
    if _engine is None:
        _engine = PersonalizationEngine()
    return _engine
