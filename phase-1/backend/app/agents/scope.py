"""Scope guard: keeps each agent inside the job it exists to do.

Every agent is narrow by design — the Class 10 Maths Tutor teaches Class 10
maths, the Social Post Image Generator renders post graphics. When a request
clearly belongs to a different agent, answering it anyway would defeat the point
of the split, so the request is *handed off* instead: the user is told which
agent owns it and can switch in one click.

The check is deliberately conservative. A handoff only happens when the selected
agent has essentially no signal for the request **and** another agent has clear
signal. Ambiguous requests stay with the selected agent, because a wrong handoff
is far more annoying than a slightly off-topic answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.catalog import AgentSpec, get_agent_spec
from app.agents.scoring import AgentScore, rank_agents, score_agent
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class ScopeVerdict:
    in_scope: bool
    own_score: float
    #: The agent that should handle it instead, when handing off.
    suggested_key: str | None = None
    suggested_name: str | None = None
    suggested_score: float = 0.0
    reason: str = ""
    alternatives: list[AgentScore] = field(default_factory=list)

    @property
    def is_handoff(self) -> bool:
        return not self.in_scope and self.suggested_key is not None


def assess(request: str, agent_key: str) -> ScopeVerdict:
    """Decide whether ``agent_key`` should answer ``request``."""
    spec = get_agent_spec(agent_key)
    text = (request or "").strip()

    own = score_agent(text, spec)

    # Too short to judge (greetings, "thanks", "ok") — never hand off.
    if len(text) < settings.SCOPE_MIN_REQUEST_CHARS:
        return ScopeVerdict(True, own.score, reason="Too short to classify; keeping the agent.")

    ranked = rank_agents(text, limit=4)
    others = [score for score in ranked if score.agent_key != spec.key]
    best_other = others[0] if others else None

    if best_other is None:
        return ScopeVerdict(True, own.score, reason="No other agent matched this request.")

    # Conservative: the selected agent must look genuinely unrelated, and the
    # alternative must be clearly better.
    own_is_weak = own.score <= settings.SCOPE_OWN_MAX_SCORE
    other_is_strong = best_other.score >= settings.SCOPE_OTHER_MIN_SCORE
    margin = best_other.score - own.score

    if own_is_weak and other_is_strong and margin >= settings.SCOPE_MIN_MARGIN:
        suggested = get_agent_spec(best_other.agent_key)
        reason = (
            f"This looks like a {suggested.name} request "
            f"({suggested.domain} domain), not {spec.name} work."
        )
        logger.info(
            "Scope handoff: %s -> %s (own=%.1f other=%.1f)",
            spec.key, suggested.key, own.score, best_other.score,
        )
        return ScopeVerdict(
            in_scope=False,
            own_score=own.score,
            suggested_key=suggested.key,
            suggested_name=suggested.name,
            suggested_score=best_other.score,
            reason=reason,
            alternatives=others[:3],
        )

    return ScopeVerdict(
        in_scope=True,
        own_score=own.score,
        reason="Within this agent's scope.",
        alternatives=others[:3],
    )


def handoff_message(spec: AgentSpec, verdict: ScopeVerdict) -> str:
    """The reply shown when a request is out of scope.

    Written as a redirect rather than a refusal: it names the right agent and
    states plainly what this one does handle.
    """
    suggested = get_agent_spec(verdict.suggested_key) if verdict.suggested_key else None
    lines = [
        f"That is outside what I do. I am the **{spec.name}** — {spec.scope}",
        "",
    ]
    if suggested:
        lines += [
            f"**{suggested.name}** handles this: {suggested.scope}",
            "",
            "Switch to it and send your message again, or ask me something in my area:",
        ]
    else:
        lines.append("Ask me something in my area:")

    lines.append("")
    lines += [f"- {example}" for example in spec.examples[:3]]
    return "\n".join(lines)


def scope_prompt_section(spec: AgentSpec) -> str:
    """The scope contract injected into every system prompt for this agent."""
    lines = [
        "=== YOUR SCOPE (do not exceed it) ===",
        f"You are the {spec.name}. You do exactly one job: {spec.scope}",
        "",
        "You do NOT handle:",
    ]
    lines += [f"- {item}" for item in spec.out_of_scope]
    lines += [
        "",
        "If a request falls outside your job, do not attempt it. Say one sentence "
        "naming what you do handle, point at the kind of agent that owns the "
        "request, and stop. Never produce a partial answer outside your scope.",
    ]
    return "\n".join(lines)
