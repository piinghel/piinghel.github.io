"""Render the published rebound snapshots, without rerunning the backtest.

Run with a Python environment containing Matplotlib. Inputs are the compact
public aggregates beside the SVGs; the source digest identifies the retained
diagnostic. All themes share one composition per viewport.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/portfolio-attribution"
METRICS = [
    ("beta", "Estimated market beta", 1, (0.65, 1.35), [0.7, 0.9, 1.1, 1.3]),
    ("ret126", "Prior stock return (%)", 100, (-65, 0), [-60, -40, -20, 0]),
    ("vol21", "Stock volatility (%)", 100, (25, 145), [40, 80, 120]),
]


def render(snapshots, dark, mobile):
    colors = {
        "bg": "#171d24" if dark else "#ffffff",
        "text": "#e4eaf0" if dark else "#263747",
        "grid": "#43505f" if dark else "#d6dfe5",
        "long": "#57bdab" if dark else "#268b7b",
        "short": "#e69482" if dark else "#bd6559",
    }
    with plt.rc_context({"font.family": "sans-serif",
                         "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none",
                         "svg.hashsalt": "attribution-holdings"}):
        fig, axes = plt.subplots(3 if mobile else 1, 1 if mobile else 3,
                                 figsize=(3.9, 8.7) if mobile else (9.6, 3.4))
        fig.set_facecolor(colors["bg"])
        for ax, (key, title, scale, limits, ticks) in zip(axes.flat, METRICS):
            ax.set_facecolor(colors["bg"])
            ax.spines[:].set_visible(False)
            ax.set_xlim(*limits)
            ax.set_ylim(-0.55, 1.65)
            ax.set_xticks(ticks)
            ax.set_yticks([1, 0], [s["date"][:4] for s in snapshots])
            ax.tick_params(length=0, labelsize=11, colors=colors["text"], pad=8)
            ax.grid(axis="x", color=colors["grid"], linewidth=0.5)
            ax.set_axisbelow(True)
            ax.set_title(title, loc="left", fontsize=12, weight="bold",
                         color=colors["text"], pad=10)
            for y, snapshot in zip([1, 0], snapshots):
                values = {s["side"]: s[key] * scale for s in snapshot["sides"]}
                ax.plot([values["long"], values["short"]], [y, y],
                        color=colors["grid"], linewidth=2, zorder=2)
                for side, marker, offset in [("long", "o", 15), ("short", "s", -20)]:
                    value = values[side]
                    assert limits[0] <= value <= limits[1]
                    label = f"{value:.2f}" if key == "beta" else f"{value:.0f}%"
                    label = label.replace("-", "−")
                    ax.plot(value, y, marker=marker, color=colors[side],
                            markersize=7, zorder=3)
                    ax.annotate(f"{side.title()}s {label}", (value, y),
                                xytext=(0, offset), textcoords="offset points",
                                ha="center", va="center", fontsize=11,
                                color=colors[side])
        fig.subplots_adjust(left=.13 if mobile else .06, right=.97,
                            top=.95 if mobile else .82, bottom=.055 if mobile else .16,
                            hspace=.55, wspace=.4)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        fig.savefig(OUTPUT / f"rebound-holdings{suffix}.svg", metadata={"Date": None})
        plt.close(fig)


if __name__ == "__main__":
    data = json.loads((OUTPUT / "rebound-holdings.json").read_text())
    for dark in [False, True]:
        for mobile in [False, True]:
            render(data["snapshots"], dark, mobile)
