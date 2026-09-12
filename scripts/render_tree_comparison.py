"""Render the forecast-quality decomposition from audited aggregate metrics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


def render(rows: list[dict], output: Path, *, dark: bool, mobile: bool) -> None:
    """Compare the same four blends, periods and metric scales in every variant."""
    colors = dict(bg="#0b1117" if dark else "#ffffff",
                  ink="#c6cdd5" if dark else "#263747",
                  grid="#39434e" if dark else "#d9e0e7",
                  full="#88b4de" if dark else "#356b9a",
                  recent="#dfaa70" if dark else "#ad7134")
    blends = [row for row in rows if row["forecast"] == "50:50"]
    if len(blends) != 4:
        raise ValueError("Expected four 50:50 blends")
    panels = [
        ("mean_ic", "Mean IC", (.045, .067), [.05, .06]),
        ("ic_std", "SD of daily IC", (.065, .125), [.07, .09, .11]),
        ("icir", "ICIR", (.45, .85), [.5, .6, .7, .8]),
    ]
    labels = [r["model"].replace("XGBoost", "XGB") if mobile else r["model"] for r in blends]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "tree-comparison"}):
        fig, axes = plt.subplots(3 if mobile else 1, 1 if mobile else 3,
                                 figsize=(4.5, 8.2) if mobile else (9.75, 3.9))
        fig.patch.set_facecolor(colors["bg"])
        for j, (ax, (metric, title, limits, ticks)) in enumerate(zip(axes, panels, strict=True)):
            ax.set_facecolor(colors["bg"])
            ax.spines[:].set_visible(False)
            ax.set_ylim(3.55, -.55)
            ax.set_yticks(range(4), labels if mobile or j == 0 else [])
            ax.tick_params(length=0, colors=colors["ink"], labelsize=12, pad=6)
            ax.grid(axis="x", color=colors["grid"], lw=.55)
            ax.set_axisbelow(True)
            ax.set_xlim(*limits)
            ax.set_xticks(ticks)
            ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=colors["ink"], pad=10)
            for y, row in enumerate(blends):
                full = row["periods"]["full_period"][metric]
                recent = row["periods"]["last_5y"][metric]
                if not all(limits[0] < value < limits[1] for value in (full, recent)):
                    raise ValueError(f"{metric} outside display scale")
                ax.plot([full, recent], [y, y], color=colors["grid"], lw=1.5)
                ax.plot(full, y, marker="o", ms=6, color=colors["full"], zorder=3)
                ax.plot(recent, y, marker="D", ms=5.3, color=colors["recent"], zorder=4)
        handles = [mlines.Line2D([], [], color=colors["full"], marker="o", ls="", label="Full history"),
                   mlines.Line2D([], [], color=colors["recent"], marker="D", ls="", label="2017–2021")]
        fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.02, .995), ncol=2,
                   frameon=False, labelcolor=colors["ink"], fontsize=12, handletextpad=.3)
        fig.subplots_adjust(left=.32 if mobile else .21, right=.975, top=.89 if mobile else .77,
                            bottom=.045 if mobile else .12, hspace=.64, wspace=.28)
        target = output / f"forecast-quality{suffix}.svg"
        fig.savefig(target, metadata={"Date": None})
        target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/tree-model-comparison")
    args = parser.parse_args()
    rows = json.loads((args.assets / "metrics.json").read_text())["rows"]
    for dark in [False, True]:
        for mobile in [False, True]:
            render(rows, args.assets, dark=dark, mobile=mobile)


if __name__ == "__main__":
    main()
