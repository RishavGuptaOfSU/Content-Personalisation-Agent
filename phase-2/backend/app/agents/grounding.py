"""Grounding guard — catches figures the user never supplied.

Marketing copy invents numbers. Measured on this project with
``llama3.2:3b``: asked to write a post about customer savings with no figure
given, the model produced "savings of up to $100K per year" in one run and
"reduce costs by up to 50%" in another, in both cases *after* being instructed
"never fabricate metrics, percentages, testimonials or customer names".

A prompt rule is not enough, for the same reason the scope contract needs the
scope guard: a small model does not reliably obey a negative instruction. So the
figures in a reply are checked against the figures that were actually available
— the request, any attachment, and the user's profiles — and anything else is
reported.

The guard **does not rewrite copy**. Silently deleting a number from a sentence
produces nonsense ("reduce costs by up to"), and the user is the one who knows
whether a claim is true. It flags, visibly and in the message metadata, and the
human decides.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from app.core.logging import get_logger

logger = get_logger(__name__)

#: Claim shapes worth checking. Plain integers are deliberately excluded: list
#: numbering, week counts, character counts and "3 variants" are not claims.
_PATTERNS: dict[str, re.Pattern[str]] = {
    # 30%, 4.5 %
    "percent": re.compile(r"\d[\d,.]*\s?%"),
    # $400, ₹1,200, €2.5k, $100K, USD 400
    "currency": re.compile(
        r"(?:[$₹€£¥]\s?\d[\d,.]*\s?(?:k|m|bn|mn|million|billion|lakh|crore)?"
        r"|\b(?:usd|inr|eur|gbp)\s?\d[\d,.]*)",
        re.IGNORECASE,
    ),
    # 10x, 3.5X — but NOT "3x per week", which is a posting cadence in a
    # channel-mix table, not a claim about outcomes.
    "multiplier": re.compile(
        r"\b\d[\d.]*\s?x\b(?!\s*(?:/|per\s|a\s|each\s|every\s)?\s*"
        r"(?:weekly|daily|monthly|quarterly|yearly|annually"
        r"|week|day|month|quarter|year|wk|mo)s?\b)",
        re.IGNORECASE,
    ),
    # "up to 40 hours", "up to 1,000 users"
    "upto": re.compile(r"\bup to\s+\d[\d,.]*", re.IGNORECASE),
}

#: A figure the agent has openly marked as its own proposal is not a fabricated
#: claim — it is a labelled suggestion, which some agents are explicitly
#: instructed to produce (the campaign planner has to propose a target KPI).
#: Matched immediately after the figure.
_LABELLED_AS_PROPOSAL = re.compile(
    r"^[\s)\]]*\(?\s*(?:suggested|suggestion|proposed|assumed|assumption|estimate[sd]?|"
    r"estimated|target|example|illustrative|placeholder|tbc|to be confirmed|hypothetical)",
    re.IGNORECASE,
)

#: Any run of digits, used to decide whether a figure was available to the model.
_NUMBER_RE = re.compile(r"\d[\d,.]*")


@dataclass(slots=True)
class GroundingReport:
    """Figures that appear in the output but were never supplied."""

    unsupported: list[str]
    #: True when the turn included an image. The guard reads text only, so a
    #: figure the model copied off a screenshot looks identical to one it made
    #: up — and calling that "an invention" would be wrong.
    had_image: bool = False

    @property
    def ok(self) -> bool:
        return not self.unsupported

    def note(self) -> str:
        """A short line appended to the reply so the user can see the risk."""
        figures = ", ".join(f"`{item}`" for item in self.unsupported[:6])
        if self.had_image:
            return (
                f"\n\n---\n⚠️ **Check these figures:** {figures}. "
                "They are not in the text you supplied. If they came from the "
                "image you attached, confirm they were read correctly — this "
                "check cannot see images."
            )
        return (
            f"\n\n---\n⚠️ **Unverified figures:** {figures}. "
            "You did not supply these, so they are the model's invention — "
            "replace them with real numbers or cut them before publishing."
        )


def _numeric_tokens(value: Any) -> set[str]:
    """Every number appearing anywhere in a value, normalised."""
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        return set().union(*(_numeric_tokens(item) for item in value)) if value else set()
    if isinstance(value, dict):
        return set().union(*(_numeric_tokens(item) for item in value.values())) if value else set()
    return {match.replace(",", "").rstrip(".") for match in _NUMBER_RE.findall(str(value))}


def available_numbers(
    *,
    request: str,
    attachment_text: str | None = None,
    profiles: Iterable[dict[str, Any]] = (),
) -> set[str]:
    """The figures the model was legitimately given."""
    numbers = _numeric_tokens(request) | _numeric_tokens(attachment_text or "")
    for profile in profiles:
        numbers |= _numeric_tokens(profile)
    return numbers


def _largest(numbers: Iterable[str]) -> float | None:
    values: list[float] = []
    for item in numbers:
        try:
            values.append(float(item))
        except ValueError:
            continue
    return max(values) if values else None


def check(
    text: str,
    *,
    supplied: set[str],
    patterns: Iterable[str],
    allow_splits_of: float | None = None,
    had_image: bool = False,
) -> GroundingReport:
    """Find claim-shaped figures in ``text`` that ``supplied`` does not justify.

    ``allow_splits_of`` handles the legitimate case where an agent divides a
    budget the user *did* give: any currency amount at or below that total is
    treated as an allocation rather than an invention. Without it, a correct
    "$200 + $100 + $100" split of a supplied $400 would be flagged.
    """
    unsupported: list[str] = []
    seen: set[str] = set()

    for name in patterns:
        pattern = _PATTERNS.get(name)
        if pattern is None:
            logger.warning("Unknown grounding pattern %r", name)
            continue
        for match in pattern.finditer(text or ""):
            figure = match.group(0).strip()
            if figure.lower() in seen:
                continue
            digits = {
                token.replace(",", "").rstrip(".") for token in _NUMBER_RE.findall(figure)
            }
            if digits & supplied:
                continue
            if name == "currency" and allow_splits_of is not None:
                value = _largest(digits)
                if value is not None and value <= allow_splits_of:
                    continue
            # "...by 20% (suggested figure)" — openly a proposal, not a claim.
            if _LABELLED_AS_PROPOSAL.match(text[match.end() : match.end() + 40]):
                continue
            seen.add(figure.lower())
            unsupported.append(figure)

    return GroundingReport(unsupported=unsupported, had_image=had_image)


__all__ = ["GroundingReport", "available_numbers", "check"]
