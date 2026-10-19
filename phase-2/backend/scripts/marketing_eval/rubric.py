"""Reads ``rubric.md`` into something a program can use.

``rubric.md`` stays the single source of truth. It is written for a person to
read, and this parses that same prose rather than keeping a second machine copy
in sync — a rubric that drifts from the one a human reads is worse than no
rubric at all.

What it expects to find, and nothing more:

* a ``## Scoring anchors`` section with lines like ``**3** — usable after edits.``
* a blockquote describing the brand context
* a ``## Dimensions`` section containing ``### <group>`` headings, each with a
  ``| Dimension | 1 | 3 | 5 |`` table whose first cell is a backticked name

Anything malformed raises. A judge that silently scores a dimension with no
anchors is just an opinion with a number attached.

    python -c "from scripts.marketing_eval.rubric import load_rubric; print(load_rubric())"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

RUBRIC_FILE = Path(__file__).resolve().parent / "rubric.md"

#: The score column headings the dimension tables use.
ANCHOR_LEVELS = (1, 3, 5)
#: The full scale a judge must choose from.
SCALE_LEVELS = (1, 2, 3, 4, 5)

_SCALE_LINE = re.compile(r"^\*\*([1-5])\*\*\s*[—–-]\s*(.+?)\s*$")
_NAME_CELL = re.compile(r"^`([a-z0-9_]+)`$")


class RubricError(ValueError):
    """Raised when rubric.md cannot be parsed, or parses into nonsense."""


@dataclass(frozen=True)
class Dimension:
    """One scored dimension and the anchors that define its scale."""

    name: str
    #: The ``### heading`` it was listed under, e.g. "Campaign planner".
    group: str
    #: ``{1: "...", 3: "...", 5: "..."}`` — what each level looks like.
    anchors: dict[int, str]

    def prompt_block(self) -> str:
        """The dimension as a judge should be shown it."""
        parts = [f"- {self.name}:"]
        for level in ANCHOR_LEVELS:
            parts.append(f"    {level} = {self.anchors[level]}")
        return "\n".join(parts)


@dataclass(frozen=True)
class Rubric:
    """The whole rubric: the scale, the brand context, and the dimensions."""

    dimensions: dict[str, Dimension]
    #: ``{1: "unusable; would be discarded.", ...}`` for all five levels.
    scale: dict[int, str]
    #: The brand blockquote, as one line of prose.
    brand_note: str
    #: Dimensions that depend on the rendered pixels, so a text-only judge
    #: must report them unjudged instead of guessing.
    visual_only: frozenset[str] = frozenset()
    source: Path = field(default=RUBRIC_FILE)

    def judgeable(self, names: list[str]) -> tuple[list[str], list[str]]:
        """Split declared dimensions into (a text judge can score, must skip)."""
        for name in names:
            self.get(name)  # validates every name, including the skipped ones
        return (
            [name for name in names if name not in self.visual_only],
            [name for name in names if name in self.visual_only],
        )

    def __contains__(self, name: object) -> bool:
        return name in self.dimensions

    def __len__(self) -> int:
        return len(self.dimensions)

    def names(self) -> list[str]:
        return list(self.dimensions)

    def get(self, name: str) -> Dimension:
        try:
            return self.dimensions[name]
        except KeyError as exc:
            raise RubricError(
                f"Unknown rubric dimension {name!r}. "
                f"Add it to {self.source.name} or fix the case that declares it."
            ) from exc

    def subset(self, names: list[str]) -> list[Dimension]:
        """The dimensions a single case declares, in the order it declared them."""
        return [self.get(name) for name in names]

    def scale_block(self) -> str:
        return "\n".join(f"    {level} = {self.scale[level]}" for level in SCALE_LEVELS)

    def groups(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for dim in self.dimensions.values():
            out.setdefault(dim.group, []).append(dim.name)
        return out


# --------------------------------------------------------------------- parse
def _split_row(line: str) -> list[str]:
    """``| a | b |`` -> ``["a", "b"]``."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell) <= {"-", ":", " "} and cell for cell in cells)


def _parse_scale(text: str) -> dict[int, str]:
    section = _section(text, "Scoring anchors")
    scale: dict[int, str] = {}
    for raw in section.splitlines():
        match = _SCALE_LINE.match(raw.strip())
        if match:
            scale[int(match.group(1))] = match.group(2)
    missing = [level for level in SCALE_LEVELS if level not in scale]
    if missing:
        raise RubricError(
            f"'Scoring anchors' is missing a description for {missing}. "
            "Each of 1-5 needs a line like '**3** — usable after edits.'"
        )
    return scale


def _parse_brand_note(text: str) -> str:
    lines = [
        line.strip().lstrip(">").strip()
        for line in text.splitlines()
        if line.strip().startswith(">")
    ]
    if not lines:
        raise RubricError(
            "No brand blockquote found. The rubric must state the brand context "
            "a judge should assume, as lines beginning with '>'."
        )
    note = " ".join(part for part in lines if part)
    # The prose is written with markdown emphasis; a prompt reads better without.
    return re.sub(r"[*_]+", "", note).strip()


def _section(text: str, heading: str) -> str:
    """The body of a ``## heading``, up to the next ``## ``."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise RubricError(f"rubric.md has no '## {heading}' section")
    return match.group(1)


def _parse_dimensions(text: str) -> dict[str, Dimension]:
    body = _section(text, "Dimensions")
    dimensions: dict[str, Dimension] = {}
    group = ""
    header_seen = False

    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            group = line[4:].strip()
            header_seen = False
            continue
        if not line.startswith("|"):
            continue

        cells = _split_row(line)
        if _is_separator(cells):
            continue
        if cells[:1] == ["Dimension"]:
            if cells[1:] != [str(level) for level in ANCHOR_LEVELS]:
                raise RubricError(
                    f"Table under '### {group}' has columns {cells!r}; expected "
                    f"Dimension plus {list(ANCHOR_LEVELS)}"
                )
            header_seen = True
            continue
        if not header_seen:
            raise RubricError(f"Table row before any header under '### {group}': {line!r}")

        name_match = _NAME_CELL.match(cells[0])
        if not name_match:
            raise RubricError(
                f"Dimension name {cells[0]!r} under '### {group}' must be a "
                "backticked lowercase identifier, e.g. `brand_tone`"
            )
        name = name_match.group(1)
        anchors = cells[1:]
        if len(anchors) != len(ANCHOR_LEVELS) or not all(anchors):
            raise RubricError(
                f"Dimension `{name}` needs a non-empty anchor for each of "
                f"{list(ANCHOR_LEVELS)}; got {anchors!r}"
            )
        if name in dimensions:
            raise RubricError(
                f"Dimension `{name}` is defined twice "
                f"(under '{dimensions[name].group}' and '{group}')"
            )
        dimensions[name] = Dimension(
            name=name,
            group=group or "(ungrouped)",
            anchors=dict(zip(ANCHOR_LEVELS, anchors, strict=True)),
        )

    if not dimensions:
        raise RubricError("No dimensions found under '## Dimensions'")
    return dimensions


def _parse_visual_only(text: str, known: dict[str, Dimension]) -> frozenset[str]:
    """Names listed under 'Dimensions a text judge must skip'.

    Optional: no section means the judge may score everything. But a name that
    does not exist is an error, because a typo here would silently re-enable
    scoring of a dimension the rubric says cannot be scored.
    """
    try:
        section = _section(text, "Dimensions a text judge must skip")
    except RubricError:
        return frozenset()

    names = re.findall(r"^\s*-\s+`([a-z0-9_]+)`", section, re.MULTILINE)
    unknown = [name for name in names if name not in known]
    if unknown:
        raise RubricError(
            f"'Dimensions a text judge must skip' lists unknown dimension(s) "
            f"{unknown}. Every name there must be defined under '## Dimensions'."
        )
    return frozenset(names)


def load_rubric(path: Path | str = RUBRIC_FILE) -> Rubric:
    """Parse rubric.md. Raises RubricError on anything it cannot read."""
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise RubricError(f"Cannot read rubric at {source}: {exc}") from exc

    dimensions = _parse_dimensions(text)
    return Rubric(
        dimensions=dimensions,
        scale=_parse_scale(text),
        brand_note=_parse_brand_note(text),
        visual_only=_parse_visual_only(text, dimensions),
        source=source,
    )


__all__ = [
    "ANCHOR_LEVELS",
    "RUBRIC_FILE",
    "SCALE_LEVELS",
    "Dimension",
    "Rubric",
    "RubricError",
    "load_rubric",
]
