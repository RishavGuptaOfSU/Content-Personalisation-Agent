"""Router Agent — picks the agent, in two stages.

Priority:
  1. **Explicit selection** from the UI always wins.
  2. **Keyword/phrase scoring** across all agents. When one agent wins clearly,
     that is the answer — no model call needed.
  3. **LLM classification** when scoring is ambiguous: first the domain, then the
     agent inside that domain. Two small decisions classify far more reliably
     than one 34-way choice.
  4. The conversation's current agent, then a sensible default.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Literal

from app.agents.catalog import (
    DOMAIN_ORDER,
    agent_exists,
    default_agent_for,
    get_agent_spec,
    get_domain,
    list_agents,
    list_domains,
)
from app.agents.scoring import AgentScore, domain_scores, rank_agents
from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import ChatMessage, LLMProviderError
from app.llm.registry import get_llm_provider

logger = get_logger(__name__)

RoutingSource = Literal[
    "explicit", "keyword_router", "llm_router", "conversation_default", "fallback"
]


@dataclass(slots=True)
class RoutingDecision:
    agent_key: str
    source: RoutingSource
    confidence: float = 0.0
    reason: str = ""
    scores: dict[str, float] = field(default_factory=dict)
    #: Runner-up agents, surfaced in the UI as "or try…".
    alternatives: list[AgentScore] = field(default_factory=list)

    @property
    def domain(self) -> str:
        return self.agent_key.split(".", 1)[0]


def _domain_prompt() -> str:
    lines = [
        "Classify the user's request into ONE domain.",
        "",
        "Domains:",
    ]
    for domain in list_domains():
        lines.append(f"- {domain.key}: {domain.description}")
    lines += [
        "",
        'Reply with ONLY JSON: {"domain": "<key>", "confidence": <0-1>}',
    ]
    return "\n".join(lines)


def _agent_prompt(domain_key: str) -> str:
    domain = get_domain(domain_key)
    lines = [
        f"Choose the ONE agent in the {domain.name} domain that owns this request.",
        "Each agent does a single job and must not do another's.",
        "",
        "Agents:",
    ]
    for spec in list_agents(domain_key):
        lines.append(f"- {spec.slug}: {spec.scope}")
        if spec.examples:
            lines.append(f"    e.g. {spec.examples[0]}")
    lines += [
        "",
        'Reply with ONLY JSON: {"agent": "<slug>", "confidence": <0-1>, "reason": "<8 words>"}',
    ]
    return "\n".join(lines)


class RouterAgent:
    name = "router"

    # --------------------------------------------------------------- public
    def route(
        self,
        request: str,
        *,
        explicit_agent: str | None = None,
        conversation_agent: str | None = None,
    ) -> RoutingDecision:
        if explicit_agent and agent_exists(explicit_agent):
            spec = get_agent_spec(explicit_agent)
            return RoutingDecision(
                agent_key=spec.key,
                source="explicit",
                confidence=1.0,
                reason="Agent selected by the user.",
            )
        if explicit_agent:
            logger.warning("Ignoring unknown explicit agent %r", explicit_agent)

        ranked = rank_agents(request, limit=5)
        scores = {item.agent_key: item.score for item in ranked}
        best = ranked[0] if ranked else None
        runner_up = ranked[1].score if len(ranked) > 1 else 0.0

        # Clear keyword winner: skip the model entirely.
        if best and best.score >= settings.ROUTER_KEYWORD_MIN_SCORE and (
            best.score - runner_up
        ) >= settings.ROUTER_LLM_MIN_MARGIN:
            return RoutingDecision(
                agent_key=best.agent_key,
                source="keyword_router",
                confidence=round(min(0.95, 0.5 + best.score / 20), 3),
                reason=f"Matched: {', '.join(best.matched[:4])}",
                scores=scores,
                alternatives=ranked[1:4],
            )

        if self.llm_routing_enabled:
            decision = self._route_with_llm(request, scores, ranked)
            if decision is not None:
                return decision

        if best and best.score > 0:
            return RoutingDecision(
                agent_key=best.agent_key,
                source="keyword_router",
                confidence=round(min(0.9, 0.4 + best.score / 20), 3),
                reason=f"Best keyword match: {', '.join(best.matched[:4]) or 'weak signal'}",
                scores=scores,
                alternatives=ranked[1:4],
            )

        if conversation_agent and agent_exists(conversation_agent):
            return RoutingDecision(
                agent_key=get_agent_spec(conversation_agent).key,
                source="conversation_default",
                confidence=0.5,
                reason="Continued with this conversation's agent.",
                scores=scores,
            )

        fallback = default_agent_for("research")
        return RoutingDecision(
            agent_key=fallback.key,
            source="fallback",
            confidence=0.25,
            reason="No clear signal; defaulted to the Concept Explainer.",
            scores=scores,
        )

    @property
    def llm_routing_enabled(self) -> bool:
        return settings.ROUTER_USE_LLM and settings.uses_real_llm

    def score(self, request: str) -> dict[str, float]:
        """Exposed for the UI/debugging."""
        return {item.agent_key: item.score for item in rank_agents(request, limit=8)}

    # -------------------------------------------------------------- private
    def _route_with_llm(
        self, request: str, scores: dict[str, float], ranked: list[AgentScore]
    ) -> RoutingDecision | None:
        domain_key = self._classify_domain(request)
        if domain_key is None:
            return None

        slug = self._classify_agent(request, domain_key)
        if slug is None:
            # Domain is known but the agent is not: use the best-scoring agent in
            # that domain, else the domain's first agent.
            in_domain = [item for item in ranked if item.domain == domain_key]
            chosen = (
                get_agent_spec(in_domain[0].agent_key)
                if in_domain
                else default_agent_for(domain_key)
            )
            return RoutingDecision(
                agent_key=chosen.key,
                source="llm_router",
                confidence=0.6,
                reason=f"LLM chose the {domain_key} domain; picked its closest agent.",
                scores=scores,
                alternatives=ranked[:3],
            )

        agent_key = f"{domain_key}.{slug}"
        if not agent_exists(agent_key):
            logger.warning("LLM returned unknown agent %r", agent_key)
            return None

        return RoutingDecision(
            agent_key=agent_key,
            source="llm_router",
            confidence=0.85,
            reason=f"LLM routed to {get_agent_spec(agent_key).name}.",
            scores=scores,
            alternatives=[item for item in ranked if item.agent_key != agent_key][:3],
        )

    def _classify_domain(self, request: str) -> str | None:
        payload = self._ask(_domain_prompt(), request)
        if not payload:
            return None
        candidate = str(payload.get("domain", "")).strip().lower()
        if candidate in DOMAIN_ORDER:
            return candidate
        # Occasionally the model answers with a name rather than a key.
        for domain in list_domains():
            if candidate and candidate in domain.name.lower():
                return domain.key
        return None

    def _classify_agent(self, request: str, domain_key: str) -> str | None:
        payload = self._ask(_agent_prompt(domain_key), request)
        if not payload:
            return None
        candidate = str(payload.get("agent", "")).strip().lower()
        valid = {spec.slug for spec in list_agents(domain_key)}
        if candidate in valid:
            return candidate
        # Tolerate a fully-qualified key.
        if "." in candidate:
            tail = candidate.split(".", 1)[1]
            if tail in valid:
                return tail
        return None

    @staticmethod
    def _ask(system_prompt: str, request: str) -> dict | None:
        try:
            response = get_llm_provider().generate(
                [ChatMessage(role="user", content=f"Request: {request[:1500]}\n\nJSON:")],
                system=system_prompt,
                temperature=settings.ROUTER_TEMPERATURE,
                max_tokens=settings.ROUTER_MAX_TOKENS,
                model=settings.router_model,
                hints={"task": "route", "request": request},
            )
        except LLMProviderError as exc:
            logger.warning("LLM routing failed (%s); using keyword scores", exc)
            return None

        match = re.search(r"\{.*}", response.content or "", re.S)
        if not match:
            return None
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None


_router: RouterAgent | None = None


def get_router() -> RouterAgent:
    global _router
    if _router is None:
        _router = RouterAgent()
    return _router


__all__ = ["RouterAgent", "RoutingDecision", "domain_scores", "get_router"]
