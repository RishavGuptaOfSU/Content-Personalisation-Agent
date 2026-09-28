"""Media generation contracts.

Agents that produce visuals return a *specification* (JSON from the model), which
a renderer turns into a real file on disk. Keeping the two apart means the model
never has to draw, and the renderer can be swapped — local Pillow rendering, a
diffusion server, or a hosted image API — without touching agent code.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Literal

Palette = Literal["brand", "dark", "light", "gradient"]
Layout = Literal["centered", "left", "split"]


@dataclass(slots=True)
class ImageSpec:
    """What to put on a generated graphic."""

    headline: str
    subline: str = ""
    badge: str = ""
    cta: str = ""
    palette: Palette = "brand"
    layout: Layout = "centered"
    alt_text: str = ""
    logo_text: str = ""
    #: Hex colours from the brand profile, most important first.
    brand_colors: list[str] = field(default_factory=list)
    width: int = 1200
    height: int = 627
    #: Free-form style token from the agent profile ("Minimal", "Dark mode"…).
    style: str = ""

    def sanitized(self) -> ImageSpec:
        def clean(value: str, limit: int) -> str:
            return " ".join(str(value or "").split())[:limit]

        self.headline = clean(self.headline, 120)
        self.subline = clean(self.subline, 200)
        self.badge = clean(self.badge, 40)
        self.cta = clean(self.cta, 40)
        self.logo_text = clean(self.logo_text, 32)
        self.alt_text = clean(self.alt_text, 300)
        self.width = max(320, min(int(self.width or 1200), 2400))
        self.height = max(180, min(int(self.height or 627), 2400))
        if self.palette not in ("brand", "dark", "light", "gradient"):
            self.palette = "brand"
        if self.layout not in ("centered", "left", "split"):
            self.layout = "centered"
        return self


@dataclass(slots=True)
class ChartSeries:
    name: str
    values: list[float]


@dataclass(slots=True)
class ChartSpec:
    """What to plot. Values come only from data the user supplied."""

    chart_type: Literal["bar", "line", "barh", "pie", "scatter", "area"] = "bar"
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    labels: list[str] = field(default_factory=list)
    series: list[ChartSeries] = field(default_factory=list)
    note: str = ""
    style: str = "Clean light"
    show_values: bool = True
    width: int = 1200
    height: int = 700

    def validate(self) -> str | None:
        """Return an error message when the spec cannot be plotted."""
        if not self.series:
            return "No data series were provided."
        if not self.labels:
            return "No category or x-axis labels were provided."
        for item in self.series:
            if not item.values:
                return f"Series {item.name!r} has no values."
            if len(item.values) != len(self.labels):
                return (
                    f"Series {item.name!r} has {len(item.values)} values but there are "
                    f"{len(self.labels)} labels — they must match."
                )
        if self.chart_type == "pie" and len(self.series) > 1:
            return "A pie chart needs exactly one series."
        return None


@dataclass(slots=True)
class RenderedMedia:
    """A file produced on disk, plus what the API needs to expose it."""

    filename: str
    url: str
    media_type: str  # "image"
    mime_type: str
    width: int
    height: int
    bytes_written: int
    alt_text: str
    renderer: str
    spec: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "url": self.url,
            "media_type": self.media_type,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "bytes": self.bytes_written,
            "alt_text": self.alt_text,
            "renderer": self.renderer,
            "spec": self.spec,
        }


class MediaGenerationError(RuntimeError):
    """Raised when a visual could not be produced."""


class BaseImageRenderer(abc.ABC):
    """Turns an :class:`ImageSpec` into a file."""

    name: str = "base"

    @abc.abstractmethod
    def render(self, spec: ImageSpec, *, filename_hint: str = "image") -> RenderedMedia: ...

    def health(self) -> dict[str, Any]:
        return {"renderer": self.name, "ok": True}
