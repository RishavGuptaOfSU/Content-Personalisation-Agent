"""Detect explicit formatting/length instructions in a user's message.

Kept in ``core`` (rather than in the agent layer) so both the personalization
engine and the agents can use it without a circular import.

These are resolved in code rather than left to the model because a
profile-derived directive ("always include a runnable example") otherwise
competes with an explicit "answer in one sentence", and smaller models resolve
that conflict badly.
"""

from __future__ import annotations

import re

_BREVITY_RE = re.compile(
    r"\b(?:in|within)?\s*(?:exactly\s+)?(?:one|1|a single|two|2)\s+"
    r"(?:sentence|line|paragraph)s?\b"
    r"|\b(?:tl;?dr|very briefly|briefly|in short|one[- ]liner|short answer)\b",
    re.I,
)
_NO_CODE_RE = re.compile(
    r"\b(?:no code|without code|no examples?|words only|prose only|"
    r"(?:don'?t|do not)\s+(?:include|write|show)\s+code)\b",
    re.I,
)
_CODE_ONLY_RE = re.compile(r"\b(?:just|only)\s+the\s+code\b|\bcode only\b", re.I)
_BULLETS_ONLY_RE = re.compile(r"\bbullets?\s*(?:only|points? only)\b", re.I)

#: Greetings and acknowledgements. These deserve a sentence, not an essay — and
#: on a local CPU model the difference is minutes.
_TRIVIAL_RE = re.compile(
    r"^\s*(?:hi|hey|hello+|yo|sup|hola|namaste|good\s+(?:morning|afternoon|evening)|"
    r"thanks?|thank\s+you|thx|ty|ok(?:ay)?|cool|nice|great|got\s+it|sounds\s+good|"
    r"bye|see\s+ya|gm|gn)\s*[!.?]*\s*$",
    re.I,
)


def detect_request_constraints(request: str) -> dict[str, bool]:
    """Flags for explicit format instructions in the current message."""
    text = request or ""
    return {
        "brevity": bool(_BREVITY_RE.search(text)),
        "no_code": bool(_NO_CODE_RE.search(text)),
        "code_only": bool(_CODE_ONLY_RE.search(text)),
        "bullets_only": bool(_BULLETS_ONLY_RE.search(text)),
        "trivial": bool(_TRIVIAL_RE.match(text.strip())),
    }


__all__ = ["detect_request_constraints"]
