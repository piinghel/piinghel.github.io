"""Render tree-model figures from audited, portfolio-level period aggregates."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

MODELS = ["XGBoost", "Shared XGBoost", "LightGBM", "Ridge"]
PERIODS = ["2002–2006", "2007–2011", "2012–2016", "2017–2021"]
LABELS = ["2002–06", "2007–11", "2012–16", "2017–21*"]


def load_rows(path: Path) -> list[dict]:
    rows = json.loads(path.read_text())["rows"]
    expected = {(m, p) for m in MODELS for p in PERIODS}
    if len(rows) != 16 or {(r["model"], r["period"]) for r in rows} != expected:
        raise ValueError("Expected all four models in all four periods")
    for row in rows:
        for key in ("mean_ic", "ic_sd", "icir", "sharpe", "annual_return_pct", "annual_vol_pct"):
            if not math.isfinite(row[key]):
                raise ValueError(f"Unavailable {key}")
        if row["ic_sd"] <= 0 or not math.isclose(row["mean_ic"] / row["ic_sd"], row["icir"], rel_tol=1e-10):
            raise ValueError("ICIR does not reconcile")
        if row["ic_start"] != row["return_start"] or row["ic_end"] != row["return_end"] or row["n_ic_dates"] != row["n_return_dates"]:
            raise ValueError("IC and portfolio dates differ")
    return rows


def render(rows: list[dict], output: Path, *, dark: bool, mobile: bool) -> None:
    ink, bg, grid = ("#c6cdd5", "#0b1117", "#39434e") if dark else ("#263747", "#ffffff", "#d9e0e7")
    palette = ["#88b4de", "#72c5ba", "#c0a3df", "#dfaa70"] if dark else ["#356b9a", "#268579", "#8060a7", "#ad7134"]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    def finish(fig, name):
        target = output / f"{name}{suffix}.svg"
        fig.savefig(target, metadata={"Date": None}, facecolor=bg)
        target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
        plt.close(fig)
    def style(ax, title):
        ax.set_facecolor(bg)
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0, colors=ink, labelsize=12, pad=6)
        ax.grid(axis="y", color=grid, lw=.55)
        ax.set_axisbelow(True)
        ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=ink, pad=12)
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "tree-comparison"}):
        fig, axes = plt.subplots(3 if mobile else 1, 1 if mobile else 3,
                                 figsize=(4.5, 8.4) if mobile else (9.75, 3.7))
        panels = [("mean_ic", "Mean IC", (.03, .073), [.04, .05, .06, .07]),
                  ("ic_sd", "SD of daily IC", (.03, .125), [.04, .06, .08, .10, .12]),
                  ("icir", "ICIR", (.4, 1.3), [.5, .75, 1, 1.25])]
        for ax, (metric, title, limits, ticks) in zip(axes, panels, strict=True):
            style(ax, title)
            ax.set_xlim(-.2, 3.2); ax.set_ylim(*limits); ax.set_yticks(ticks)
            ax.set_xticks(range(4), ["02–06", "07–11", "12–16", "17–21*"])
            for i, model in enumerate(MODELS):
                vals = [next(r[metric] for r in rows if r["model"] == model and r["period"] == period) for period in PERIODS]
                if not all(limits[0] < v < limits[1] for v in vals):
                    raise ValueError(f"{metric} outside scale")
                ax.plot(range(4), vals, color=palette[i], lw=1.4, ls=["-", "--", ":", "-"][i],
                        marker=["o", "s", "D", "^"][i], ms=4, alpha=.9)
        handles = [mlines.Line2D([], [], color=palette[i], marker=["o", "s", "D", "^"][i],
                                ls=["-", "--", ":", "-"][i], label=m.replace("XGBoost", "XGB")) for i, m in enumerate(MODELS)]
        fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.07, .995), ncol=2 if mobile else 4,
                   frameon=False, labelcolor=ink, fontsize=12, handlelength=1.8, handletextpad=.5)
        fig.subplots_adjust(left=.16 if mobile else .065, right=.97, top=.87 if mobile else .76,
                            bottom=.045 if mobile else .14, hspace=.65, wspace=.36)
        finish(fig, "forecast-quality")

        fig, axes = plt.subplots(4 if mobile else 2, 1 if mobile else 2,
                                 figsize=(4.5, 11.6) if mobile else (9.75, 6.3))
        panels = [("sharpe", "icir", "ICIR", "Portfolio Sharpe (annualized)", (.55, 2.45), (.35, 1.3)),
                  ("annual_return_pct", "ic_sd", "SD of daily IC", "Mean daily net return (bp)", (1.5, 7.1), (.02, .13))]
        for k, model in enumerate(["LightGBM", "Ridge"]):
            for j, (xkey, ykey, ytitle, xtitle, xlim, ylim) in enumerate(panels):
                ax = axes.flat[k * 2 + j]
                style(ax, f"{model} · {ytitle}")
                ax.set_xlim(*xlim); ax.set_ylim(*ylim)
                ax.set_xlabel(xtitle, color=ink, fontsize=12, labelpad=10)
                if j == 0:
                    ax.set_xticks([.75, 1.25, 1.75, 2.25]); ax.set_yticks([.5, .75, 1, 1.25])
                else:
                    ax.set_xticks([2, 3.5, 5, 6.5]); ax.set_yticks([.03, .06, .09, .12])
                for i, period in enumerate(PERIODS):
                    row = next(r for r in rows if r["model"] == model and r["period"] == period)
                    x, y = row[xkey] * (100 / 252 if j == 1 else 1), row[ykey]
                    if not (xlim[0] < x < xlim[1] and ylim[0] < y < ylim[1]):
                        raise ValueError("Association point outside scale")
                    ax.plot(x, y, marker=["o", "s", "D", "^"][i], color=palette[MODELS.index(model)], ms=6, ls="")
                    dy = -16 if i == 1 or (i == 0 and j == 1) else 12
                    ax.annotate(LABELS[i], (x, y), xytext=(0, dy), textcoords="offset points",
                                ha="center", va="center", fontsize=11, color=ink)
        fig.subplots_adjust(left=.16 if mobile else .075, right=.97, top=.96 if mobile else .92,
                            bottom=.055 if mobile else .1, hspace=.69, wspace=.3)
        finish(fig, "forecast-outcomes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/tree-model-comparison")
    args = parser.parse_args()
    rows = load_rows(args.assets / "period-metrics.json")
    for dark in [False, True]:
        for mobile in [False, True]:
            render(rows, args.assets, dark=dark, mobile=mobile)


if __name__ == "__main__":
    main()
