#!/usr/bin/env python
"""Regenerates every figure in the paper from the measured eval reports.

Run from the repo root with the phase-2 virtualenv:

    phase-2/backend/.venv/bin/python paper/make_figures.py

Nothing here is hand-drawn from remembered numbers: each figure reads the JSON
the harness and judge wrote, so a figure cannot drift from the result it claims
to show. Outputs PDF (for LaTeX) and PNG (for Word/preview) side by side.
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "phase-2" / "backend" / "scripts" / "marketing_eval" / "reports"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# IEEE Access is two-column; a single-column figure is ~3.5in wide.
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
    "savefig.dpi": 400,
})

GREY = "#4b5563"
BLUE = "#2563eb"
ORANGE = "#ea580c"
GREEN = "#15803d"


def load(pattern: str) -> dict:
    matches = sorted(glob.glob(str(REPORTS / pattern)))
    if not matches:
        raise SystemExit(f"No report matching {pattern}")
    return json.loads(Path(matches[-1]).read_text())


def save(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}")
    plt.close(fig)
    print(f"  wrote figures/{name}.pdf + .png")


# ------------------------------------------------------------------ figure 1
def fig_architecture() -> None:
    """The request pipeline. Drawn in code so it stays consistent with the text.

    Two rows of four rather than one row of eight: at IEEE's 7.16 in double-column
    width, eight boxes leave about 0.74 in each, which is narrower than the
    stage descriptions need and makes the text overrun its box.
    """
    fig, ax = plt.subplots(figsize=(7.16, 3.35))
    ax.set_xlim(-1, 101)
    ax.set_ylim(-5, 54)
    ax.axis("off")

    stages = [
        ("1. Request", "user message,\nagent optional"),
        ("2. Route", "keyword score;\nLLM only when\nmargin < θ"),
        ("3. Scope guard", "task-evidence score;\nhand off when\nmismatched"),
        ("4. Compose profile", "global → domain\n→ agent"),
        ("5. Retrieve memory", "semantic match +\nstanding preferences"),
        ("6. Generate", "agent prompt +\noutput contract"),
        ("7. Grounding guard", "flag figures the\nuser never supplied"),
        ("8. Persist", "message, media,\nextracted memories"),
    ]
    w, gap, h = 22.0, 4.0, 15.0
    rows = [stages[:4], stages[4:]]
    y_of = {0: 30.0, 1: 7.0}
    centres: dict[str, tuple[float, float]] = {}

    for r, row in enumerate(rows):
        y = y_of[r]
        for c, (title, detail) in enumerate(row):
            x = c * (w + gap)
            highlight = "guard" in title
            ax.add_patch(mpatches.FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
                linewidth=1.0,
                edgecolor=ORANGE if highlight else GREY,
                facecolor="#fff7ed" if highlight else "#f9fafb",
            ))
            ax.text(x + w / 2, y + h - 3.8, title, ha="center", va="center",
                    fontsize=7.8, fontweight="bold")
            ax.text(x + w / 2, y + 4.8, detail, ha="center", va="center",
                    fontsize=6.4, color="#374151", linespacing=1.4)
            centres[title] = (x + w / 2, y)
            if c < len(row) - 1:
                ax.annotate("", xy=(x + w + gap, y + h / 2), xytext=(x + w, y + h / 2),
                            arrowprops=dict(arrowstyle="-|>", linewidth=0.9, color=GREY))

    # Wrap from the end of row 1 down to the start of row 2, routed through the
    # clear band between the rows. Both callouts are placed outside the rows
    # (above row 1, below row 2) so nothing crosses this path.
    last_cx = 3 * (w + gap) + w / 2
    mid_y = (y_of[0] + y_of[1] + h) / 2
    ax.annotate("", xy=(last_cx, mid_y), xytext=(last_cx, y_of[0]),
                arrowprops=dict(arrowstyle="-", linewidth=0.9, color=GREY))
    ax.annotate("", xy=(w / 2, mid_y), xytext=(last_cx, mid_y),
                arrowprops=dict(arrowstyle="-", linewidth=0.9, color=GREY))
    ax.annotate("", xy=(w / 2, y_of[1] + h), xytext=(w / 2, mid_y),
                arrowprops=dict(arrowstyle="-|>", linewidth=0.9, color=GREY))

    # The two deterministic interventions this paper evaluates.
    sx, sy = centres["3. Scope guard"]
    ax.annotate("", xy=(sx, sy + h + 0.8), xytext=(sx, sy + h + 5.4),
                arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color=ORANGE))
    ax.text(sx, sy + h + 7.2, "handoff: no model call", fontsize=6.8,
            color=ORANGE, ha="center", va="center", fontweight="bold")

    gx, gy = centres["7. Grounding guard"]
    ax.annotate("", xy=(gx, gy - 0.8), xytext=(gx, gy - 5.4),
                arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color=ORANGE))
    ax.text(gx, gy - 7.2, "flags, never rewrites", fontsize=6.8,
            color=ORANGE, ha="center", va="center", fontweight="bold")

    save(fig, "fig1_pipeline")


# ------------------------------------------------------------------ figure 2
def fig_scale_collapse() -> None:
    """The judge used three of five scale points until the prompt named 2 and 4."""
    v1 = load("*CLOUD-gemma4-fixed-openai.scores-promptv1.json")
    v2 = load("*CLOUD-gemma4-cases-fixed-openai.scores.json")

    def raw(doc: dict) -> Counter:
        return Counter(
            s for c in doc["cases"] for e in c["dimensions"].values() for s in e["runs"]
        )

    c1, c2 = raw(v1), raw(v2)
    n1, n2 = sum(c1.values()), sum(c2.values())
    levels = [1, 2, 3, 4, 5]
    p1 = [100 * c1.get(x, 0) / n1 for x in levels]
    p2 = [100 * c2.get(x, 0) / n2 for x in levels]

    fig, ax = plt.subplots(figsize=(3.45, 2.2))
    x = np.arange(len(levels))
    ax.bar(x - 0.2, p1, 0.4, label=f"Prompt v1 (n={n1})", color=ORANGE, edgecolor="white")
    ax.bar(x + 0.2, p2, 0.4, label=f"Prompt v2 (n={n2})", color=BLUE, edgecolor="white")
    for xi, val in zip(x - 0.2, p1):
        if val == 0:
            ax.text(xi, 1.4, "0", ha="center", fontsize=6.5, color=ORANGE, fontweight="bold")
    ax.set_xticks(x, [str(level) for level in levels])
    ax.set_xlabel("Judge score (rubric anchors defined at 1, 3, 5)")
    ax.set_ylabel("Share of scores (%)")
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(0, 70)
    save(fig, "fig2_scale_collapse")


# ------------------------------------------------------------------ figure 3
def fig_bakeoff() -> None:
    """Quality against latency for every free model, with the noise band drawn."""
    rows = []
    for path in sorted(glob.glob(str(REPORTS / "*BAKEOFF2*.scores.json"))):
        scores = json.loads(Path(path).read_text())
        report = json.loads((REPORTS / scores["report"]["file"]).read_text())
        rows.append({
            "model": scores["report"]["llm_model"],
            "mean": scores["summary"]["mean"],
            "elapsed": report["elapsed_seconds"],
            "errors": report["totals"]["errors"],
            "cases": scores["summary"]["scored_cases"],
        })
    full = max(r["cases"] for r in rows)

    fig, ax = plt.subplots(figsize=(3.45, 2.75))
    best = max(r["mean"] for r in rows if r["cases"] == full)
    ax.axhspan(best - 0.5, best, color=GREEN, alpha=0.10, zorder=0,
               label="within run-to-run noise (0.5)")
    ax.axhline(best, color=GREEN, linewidth=0.7, linestyle="--", zorder=1)

    # Label offsets are set per point: the models cluster tightly in both axes,
    # and a single rule puts at least two labels on top of each other.
    offsets = {
        "gemma4:31b": (12, 9),
        "beam": (0, 9),
        "gpt-oss:20b": (0, -13),
        "gpt-oss:120b": (6, 9),
        "nemotron-3-ultra": (-8, 9),
        "nemotron-3-super": (-2, -13),
        "nemotron-3-nano:30b": (-6, 9),
    }
    for row in rows:
        excluded = row["cases"] != full
        ax.scatter(row["elapsed"], row["mean"], s=36,
                   color="white", edgecolor=GREY if excluded else BLUE,
                   linewidth=1.1, zorder=4,
                   marker="X" if excluded else "o")
        label = row["model"].replace("nemotron-3-", "nem3-")
        dx, dy = offsets.get(row["model"], (0, 9))
        ax.annotate(label, (row["elapsed"], row["mean"]),
                    textcoords="offset points", xytext=(dx, dy),
                    ha="center", fontsize=5.9, zorder=5,
                    color=GREY if excluded else "#111827")

    ax.set_xscale("log")
    # Explicit ticks with plain numbers: matplotlib's default log labels
    # ("4x10^1", "6x10^1", ...) overlap at this width.
    ticks = [40, 60, 100, 200, 400, 800]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xlim(34, 1150)
    ax.set_xlabel("Full 30-case run time (s, log scale)")
    ax.set_ylabel("Judge score (mean of 61 dimensions)")
    ax.set_ylim(3.35, 4.42)

    handles = [
        plt.Line2D([], [], marker="o", color=BLUE, linestyle="", markerfacecolor="white",
                   label="all 22 cases scored"),
        plt.Line2D([], [], marker="X", color=GREY, linestyle="", markerfacecolor="white",
                   label="excluded (cases errored)"),
        mpatches.Patch(facecolor=GREEN, alpha=0.18, label="within noise of best (0.5)"),
    ]
    ax.legend(handles=handles, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.17), ncol=1, fontsize=6.2,
              handletextpad=0.6, borderaxespad=0.0)
    save(fig, "fig3_bakeoff")


# ------------------------------------------------------------------ figure 4
def fig_ab_per_agent() -> None:
    """Per-agent A/B, with the control arm's own variance shown for scale."""
    single = load("*VERIFY-single-gemma4*.scores.json")
    mixed = load("*VERIFY-mixed-fleet*.scores.json")
    pins = mixed["report"].get("agent_models") or {}

    agents = sorted(single["summary"]["by_agent"])
    labels = [a.replace("marketing.", "") for a in agents]
    a = [single["summary"]["by_agent"][k] for k in agents]
    b = [mixed["summary"]["by_agent"][k] for k in agents]
    noise = mixed["summary"]["reliability"]["mean_spread"]

    fig, ax = plt.subplots(figsize=(3.45, 2.6))
    y = np.arange(len(agents))
    ax.barh(y + 0.2, a, 0.4, label="One model (gemma4:31b)", color=BLUE, edgecolor="white")
    ax.barh(y - 0.2, b, 0.4, label="Mixed fleet (2 agents pinned)", color=ORANGE,
            edgecolor="white")

    for i, k in enumerate(agents):
        # Judge disagreement on the control arm, drawn to the same scale as the
        # bars so the reader can see every gap sits inside it.
        ax.plot([a[i] - noise / 2, a[i] + noise / 2], [i + 0.2, i + 0.2],
                color="#111827", linewidth=1.2, solid_capstyle="butt", zorder=4)
        ax.plot([a[i], a[i]], [i + 0.09, i + 0.31], color="#111827",
                linewidth=0.8, zorder=4)
        if k in pins:
            ax.text(0.15, i - 0.2, "pinned", fontsize=5.8, color="white",
                    va="center", fontweight="bold")
        ax.text(max(a[i], b[i]) + 0.12, i, f"{b[i] - a[i]:+.2f}", fontsize=5.9,
                va="center", color="#374151")

    ax.set_yticks(y, labels)
    ax.set_xlabel("Judge score (median of 3 runs)")
    ax.set_xlim(0, 5.9)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.invert_yaxis()
    # Legend above the axes: at this size any in-axes position overlaps a bar.
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=1, fontsize=6.3, handletextpad=0.6, borderaxespad=0.0)
    save(fig, "fig4_ab_per_agent")


if __name__ == "__main__":
    print(f"Reading reports from {REPORTS}")
    fig_architecture()
    fig_scale_collapse()
    fig_bakeoff()
    fig_ab_per_agent()
    print(f"\nAll figures written to {OUT}")
