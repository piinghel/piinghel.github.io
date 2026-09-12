"""Render compact portfolio and ranking comparisons from audited aggregate metrics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np


def render(rows: list[dict], output: Path, *, dark: bool, mobile: bool) -> None:
    """Keep row order, value scales and period encoding identical across variants."""
    colors = dict(bg="#0b1117" if dark else "#ffffff",
                  ink="#c6cdd5" if dark else "#263747",
                  grid="#39434e" if dark else "#d9e0e7",
                  full="#88b4de" if dark else "#356b9a",
                  recent="#dfaa70" if dark else "#ad7134")
    ys = np.array([0, 1, 2, 3, 4.5, 5.5, 7, 8, 9.5, 10.5])
    labels = [f"{r['model']} {r['forecast']}" for r in rows]
    if mobile:
        labels = [s.replace("Shared XGBoost", "Shared XGB").replace("XGBoost", "XGB")
                  .replace(" days", "d") for s in labels]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"], "font.size": 11 if mobile else 12,
                         "svg.fonttype": "none", "svg.hashsalt": "tree-comparison"}):
        for name in ["portfolio-sharpe", "forecast-quality"]:
            quality = name == "forecast-quality"
            fig, axes = plt.subplots(1, 2 if quality else 1,
                                     figsize=(4.5, 5.1) if mobile else (9.75, 5.8),
                                     squeeze=False)
            fig.patch.set_facecolor(colors["bg"])
            for j, ax in enumerate(axes[0]):
                ax.set_facecolor(colors["bg"])
                ax.spines[:].set_visible(False)
                ax.set_ylim(11.25, -0.8)
                ax.set_yticks(ys, labels if j == 0 else [])
                ax.tick_params(length=0, colors=colors["ink"], labelsize=10.5 if mobile else 12, pad=5)
                ax.grid(axis="x", color=colors["grid"], lw=0.55)
                ax.set_axisbelow(True)
                ax.axhline(3.75, color=colors["grid"], lw=0.65)
                metric = "mean_ic" if quality and j == 0 else "icir" if quality else "sharpe_ratio"
                if metric == "mean_ic":
                    limits, ticks, title = (0.039, 0.063), [0.04, 0.05, 0.06], "Mean IC"
                elif metric == "icir":
                    limits, ticks, title = (0.40, 0.85), [0.4, 0.6, 0.8], "ICIR"
                else:
                    limits, ticks, title = (1.1, 2.2), [1.2, 1.5, 1.8, 2.1], "Net portfolio Sharpe"
                ax.set_xlim(*limits)
                ax.set_xticks(ticks)
                ax.set_title(title, loc="left", fontsize=12 if mobile else 14,
                             fontweight="bold", color=colors["ink"], pad=12)
                for y, row in zip(ys, rows, strict=True):
                    full = row["periods"]["full_period"][metric]
                    assert limits[0] < full < limits[1], (name, full)
                    if metric != "mean_ic":
                        recent = row["periods"]["last_5y"][metric]
                        assert limits[0] < recent < limits[1], (name, recent)
                        ax.plot([full, recent], [y, y], color=colors["grid"], lw=1.4, zorder=2)
                        ax.plot(recent, y, marker="D", ms=4.8, color=colors["recent"], zorder=4)
                    ax.plot(full, y, marker="o", ms=5.5, color=colors["full"], zorder=3)
            handles = [mlines.Line2D([], [], color=colors["full"], marker="o", ls="", label="Full history"),
                       mlines.Line2D([], [], color=colors["recent"], marker="D", ls="", label="2017–2021")]
            fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02 if mobile else .025, .995),
                       ncol=2, frameon=False, labelcolor=colors["ink"], fontsize=11 if mobile else 12,
                       handletextpad=.3, columnspacing=1.1)
            fig.subplots_adjust(left=.34 if mobile else .30, right=.97, top=.83 if mobile else .84,
                                bottom=.075, wspace=.38 if mobile else .25)
            target = output / f"{name}{suffix}.svg"
            fig.savefig(target, metadata={"Date": None})
            target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
            plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/tree-model-comparison")
    args = parser.parse_args()
    rows = json.loads((args.assets / "metrics.json").read_text())["rows"]
    if len(rows) != 10 or len({(r["model"], r["forecast"]) for r in rows}) != 10:
        raise ValueError("Expected ten unique model/forecast comparisons")
    for dark in [False, True]:
        for mobile in [False, True]:
            render(rows, args.assets, dark=dark, mobile=mobile)


if __name__ == "__main__":
    main()
