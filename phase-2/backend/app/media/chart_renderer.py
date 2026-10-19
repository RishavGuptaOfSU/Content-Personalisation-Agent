"""Chart rendering with matplotlib.

The Chart Builder agent returns a chart *specification* built only from data the
user supplied; this turns it into a PNG. Nothing here invents data points.
"""

from __future__ import annotations

from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless: no display server needed
import matplotlib.pyplot as plt  # noqa: E402

from app.core.logging import get_logger  # noqa: E402
from app.media.base import ChartSpec, MediaGenerationError, RenderedMedia  # noqa: E402
from app.media.storage import build_filename, media_path, prune_media, public_url  # noqa: E402

logger = get_logger(__name__)

_STYLES: dict[str, dict[str, Any]] = {
    "clean light": {
        "face": "#ffffff",
        "axes": "#ffffff",
        "text": "#0f172a",
        "grid": "#e2e8f0",
        "colors": ["#4f46e5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
    },
    "dark": {
        "face": "#020617",
        "axes": "#0f172a",
        "text": "#e2e8f0",
        "grid": "#1e293b",
        "colors": ["#818cf8", "#38bdf8", "#34d399", "#fbbf24", "#f87171", "#c084fc"],
    },
    "minimal": {
        "face": "#ffffff",
        "axes": "#ffffff",
        "text": "#111827",
        "grid": "#f1f5f9",
        "colors": ["#111827", "#6b7280", "#9ca3af", "#d1d5db"],
    },
    "colourful": {
        "face": "#ffffff",
        "axes": "#ffffff",
        "text": "#0f172a",
        "grid": "#e5e7eb",
        "colors": ["#ec4899", "#8b5cf6", "#06b6d4", "#84cc16", "#f97316", "#14b8a6"],
    },
}


def _style_for(name: str) -> dict[str, Any]:
    key = (name or "").strip().lower()
    if key in _STYLES:
        return _STYLES[key]
    if "dark" in key:
        return _STYLES["dark"]
    if "minimal" in key:
        return _STYLES["minimal"]
    if "colour" in key or "color" in key:
        return _STYLES["colourful"]
    return _STYLES["clean light"]


class ChartRenderer:
    """Renders a :class:`ChartSpec` to a PNG file."""

    name = "matplotlib"

    def render(self, spec: ChartSpec, *, filename_hint: str = "chart") -> RenderedMedia:
        problem = spec.validate()
        if problem:
            raise MediaGenerationError(problem)

        style = _style_for(spec.style)
        dpi = 100
        figure, axes = plt.subplots(
            figsize=(spec.width / dpi, spec.height / dpi),
            dpi=dpi,
            facecolor=style["face"],
        )
        axes.set_facecolor(style["axes"])

        try:
            self._plot(axes, spec, style)
            self._decorate(axes, spec, style)
            figure.tight_layout(pad=2.0)

            filename = build_filename(filename_hint)
            path = media_path(filename)
            figure.savefig(path, format="png", facecolor=style["face"], bbox_inches="tight")
        finally:
            plt.close(figure)

        prune_media()
        alt = spec.note or f"{spec.chart_type} chart titled {spec.title or 'untitled'}"
        logger.info("Rendered chart %s (%s)", filename, spec.chart_type)
        return RenderedMedia(
            filename=filename,
            url=public_url(filename),
            media_type="image",
            mime_type="image/png",
            width=spec.width,
            height=spec.height,
            bytes_written=path.stat().st_size,
            alt_text=alt,
            renderer=self.name,
            spec={
                "chart_type": spec.chart_type,
                "title": spec.title,
                "labels": spec.labels,
                "series": [{"name": s.name, "values": s.values} for s in spec.series],
                "note": spec.note,
            },
        )

    # ------------------------------------------------------------- internals
    def _plot(self, axes, spec: ChartSpec, style: dict[str, Any]) -> None:
        colors = style["colors"]
        labels = spec.labels
        positions = range(len(labels))

        if spec.chart_type == "pie":
            series = spec.series[0]
            wedges, texts, autotexts = axes.pie(
                series.values,
                labels=labels,
                autopct="%1.1f%%" if spec.show_values else None,
                colors=colors[: len(labels)],
                startangle=90,
                wedgeprops={"edgecolor": style["face"], "linewidth": 2},
            )
            for text in texts + (autotexts or []):
                text.set_color(style["text"])
            axes.axis("equal")
            return

        if spec.chart_type in ("line", "area"):
            for index, series in enumerate(spec.series):
                color = colors[index % len(colors)]
                axes.plot(
                    positions, series.values, marker="o", linewidth=2.4,
                    color=color, label=series.name,
                )
                if spec.chart_type == "area":
                    axes.fill_between(positions, series.values, alpha=0.18, color=color)
                # "Show values" is a profile promise, so honour it for lines too —
                # not only for bars, where bar_label does it for free.
                if spec.show_values:
                    for x, y in zip(positions, series.values):
                        axes.annotate(
                            self._format_value(y),
                            (x, y),
                            textcoords="offset points",
                            xytext=(0, 8),
                            ha="center",
                            fontsize=9,
                            color=style["text"],
                        )
            axes.set_xticks(list(positions))
            axes.set_xticklabels(labels, rotation=30 if max(map(len, labels), default=0) > 8 else 0,
                                 ha="right" if max(map(len, labels), default=0) > 8 else "center")

        elif spec.chart_type == "scatter":
            for index, series in enumerate(spec.series):
                axes.scatter(
                    positions, series.values, s=90,
                    color=colors[index % len(colors)], label=series.name, alpha=0.85,
                )
                if spec.show_values:
                    for x, y in zip(positions, series.values):
                        axes.annotate(
                            self._format_value(y),
                            (x, y),
                            textcoords="offset points",
                            xytext=(0, 9),
                            ha="center",
                            fontsize=9,
                            color=style["text"],
                        )
            axes.set_xticks(list(positions))
            axes.set_xticklabels(labels)

        elif spec.chart_type == "barh":
            count = len(spec.series)
            thickness = 0.8 / count
            for index, series in enumerate(spec.series):
                offsets = [p + index * thickness for p in positions]
                bars = axes.barh(
                    offsets, series.values, height=thickness,
                    color=colors[index % len(colors)], label=series.name,
                )
                if spec.show_values:
                    axes.bar_label(bars, padding=3, color=style["text"], fontsize=9)
            axes.set_yticks([p + thickness * (count - 1) / 2 for p in positions])
            axes.set_yticklabels(labels)

        else:  # bar
            count = len(spec.series)
            width = 0.8 / count
            for index, series in enumerate(spec.series):
                offsets = [p + index * width for p in positions]
                bars = axes.bar(
                    offsets, series.values, width=width,
                    color=colors[index % len(colors)], label=series.name,
                )
                if spec.show_values:
                    axes.bar_label(bars, padding=3, color=style["text"], fontsize=9)
            axes.set_xticks([p + width * (count - 1) / 2 for p in positions])
            axes.set_xticklabels(
                labels,
                rotation=30 if max(map(len, labels), default=0) > 8 else 0,
                ha="right" if max(map(len, labels), default=0) > 8 else "center",
            )

        axes.grid(axis="y" if spec.chart_type != "barh" else "x",
                  color=style["grid"], linewidth=1, alpha=0.9)
        axes.set_axisbelow(True)

    @staticmethod
    def _format_value(value: float) -> str:
        """Drop a pointless trailing ``.0`` so 120.0 reads as 120."""
        return f"{value:g}"

    @staticmethod
    def _decorate(axes, spec: ChartSpec, style: dict[str, Any]) -> None:
        if spec.title:
            axes.set_title(spec.title, color=style["text"], fontsize=15, fontweight="bold", pad=16)
        if spec.x_label and spec.chart_type != "pie":
            axes.set_xlabel(spec.x_label, color=style["text"], fontsize=11)
        if spec.y_label and spec.chart_type != "pie":
            axes.set_ylabel(spec.y_label, color=style["text"], fontsize=11)

        axes.tick_params(colors=style["text"], labelsize=10)
        for spine_name, spine in axes.spines.items():
            spine.set_visible(spine_name in ("left", "bottom") and spec.chart_type != "pie")
            spine.set_color(style["grid"])

        if len(spec.series) > 1:
            legend = axes.legend(frameon=False, fontsize=10)
            for text in legend.get_texts():
                text.set_color(style["text"])


_renderer: ChartRenderer | None = None


def get_chart_renderer() -> ChartRenderer:
    global _renderer
    if _renderer is None:
        _renderer = ChartRenderer()
    return _renderer
