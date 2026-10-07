"""Relevance scoring shared by the router and the scope guard.

One scoring function, two uses: the router picks the highest scoring agent for a
request, and the scope guard checks whether the *selected* agent is a plausible
owner of the request or whether another agent clearly owns it instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.catalog import AgentSpec, list_agents

_WORD_RE = re.compile(r"[a-z0-9+#.\-']+")

#: Weights chosen so a single multi-word phrase outranks incidental single words.
_PHRASE_WEIGHT = 3.0
_WORD_WEIGHT = 1.0
_NAME_WEIGHT = 2.0
_EXAMPLE_WEIGHT = 0.6
_DOMAIN_WEIGHT = 1.5

_STOPWORDS = frozenset(
    """a an the and or but for of to in on with without at by from as is are was were be been
    being do does did doing have has had having i me my we our you your it its this that these
    those what which who how why when where can could should would will shall may might must
    please help need want give show tell make write create explain about into over under
    """.split()
)


def _normalize(word: str) -> str:
    """Fold simple plurals so "MCQs" matches the keyword "mcq"."""
    if len(word) > 3 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("es") and not word.endswith("ses"):
        return word[:-2]
    if len(word) > 2 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokens(text: str) -> set[str]:
    """Content tokens, plus a normalised form of each for plural-insensitive hits."""
    words = [
        word
        for word in _WORD_RE.findall((text or "").lower())
        if word not in _STOPWORDS and len(word) > 1
    ]
    return set(words) | {_normalize(word) for word in words}


@dataclass(slots=True)
class AgentScore:
    agent_key: str
    score: float
    matched: list[str]

    @property
    def domain(self) -> str:
        return self.agent_key.split(".", 1)[0]


def score_agent(request: str, spec: AgentSpec) -> AgentScore:
    """How strongly ``request`` looks like this agent's job."""
    text = (request or "").lower()
    tokens = _tokens(text)
    score = 0.0
    matched: list[str] = []

    for keyword in spec.keywords:
        key = keyword.lower()
        if " " in key:
            if key in text:
                score += _PHRASE_WEIGHT
                matched.append(keyword)
        elif key in tokens or _normalize(key) in tokens:
            score += _WORD_WEIGHT
            matched.append(keyword)

    # The agent's own name is strong evidence ("quiz generator", "resume") — but
    # skip bare numbers, or every "10" in a request would match "Class 10 Maths".
    for word in _tokens(spec.name):
        if word.isdigit() or word in ("tutor", "agent", "generator", "writer"):
            continue
        if word in tokens:
            score += _NAME_WEIGHT
            matched.append(word)

    # Overlap with the example requests captures phrasing the keywords miss.
    for example in spec.examples:
        overlap = _tokens(example) & tokens
        if len(overlap) >= 2:
            score += _EXAMPLE_WEIGHT * len(overlap)
            matched.extend(sorted(overlap)[:3])

    if spec.domain in tokens:
        score += _DOMAIN_WEIGHT
        matched.append(spec.domain)

    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique = [m for m in matched if not (m in seen or seen.add(m))]
    return AgentScore(agent_key=spec.key, score=round(score, 3), matched=unique[:8])


def rank_agents(request: str, *, domain: str | None = None, limit: int = 5) -> list[AgentScore]:
    """Best-matching agents for a request, highest first, zero scores dropped."""
    scores = [score_agent(request, spec) for spec in list_agents(domain)]
    scores = [s for s in scores if s.score > 0]
    scores.sort(key=lambda s: s.score, reverse=True)
    return scores[:limit]


def domain_scores(request: str) -> dict[str, float]:
    """Aggregate agent scores per domain — used for two-stage routing."""
    totals: dict[str, float] = {}
    for score in (score_agent(request, spec) for spec in list_agents()):
        if score.score <= 0:
            continue
        # Best agent dominates; other agents in the domain add a little support.
        current = totals.get(score.domain, 0.0)
        totals[score.domain] = max(current, score.score) + min(current, score.score) * 0.15
    return {key: round(value, 3) for key, value in totals.items()}
