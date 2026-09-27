"""Tree-model article: LightGBM's growth relative to Ridge on the same 80 predictors.

`--sweep` reads growth_drawdown.csv from factor_combination's sweep_review.py output
(outputs/matched_80_20260926/tree_comparison_2026_09_27/sweep) and writes the
aggregate ratio path to assets/tree-model-comparison/relative-growth.json;
rendering reads only that file.
"""

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

OUTPUT = Path(__file__).resolve().parents[1] / "assets/tree-model-comparison"
LATER_START = dt.date(2022, 1, 1)


def export(sweep: Path) -> None:
    paths: dict[str, dict[str, float]] = {}
    with (sweep / "growth_drawdown.csv").open() as source:
        for row in csv.DictReader(source):
            paths.setdefault(row["model"], {})[row["date"]] = float(row["growth_index"])
    dates = sorted(set(paths["lightgbm"]) & set(paths["ridge"]))
    ratio = [paths["lightgbm"][d] / paths["ridge"][d] for d in dates]
    (OUTPUT / "relative-growth.json").write_text(
        json.dumps({"dates": dates, "lightgbm_over_ridge": ratio}, separators=(",", ":")) + "\n"
    )


def render(data: dict, dark: bool, mobile: bool) -> None:
    colors = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4eaf0" if dark else "#263747",
        "grid": "#43505f" if dark else "#d6dfe5",
        "line": "#76b3d4" if dark else "#32759a",
        "shade": "#1b222b" if dark else "#f1f3f5",
        "muted": "#9aa6af" if dark else "#5d6b76",
    }
    dates = [dt.date.fromisoformat(d) for d in data["dates"]]
    ratio = data["lightgbm_over_ridge"]
    size = 11 if mobile else 11.5
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "tree-comparison"}):
        fig, ax = plt.subplots(figsize=(4.4, 3.6) if mobile else (8.4, 3.8))
        fig.set_facecolor(colors["bg"])
        ax.set_facecolor(colors["bg"])
        ax.axvspan(LATER_START, dates[-1], color=colors["shade"], linewidth=0, zorder=0)
        ax.axhline(1, color=colors["grid"], linewidth=0.9, zorder=1)
        ax.plot(dates, ratio, color=colors["line"], linewidth=1.3, zorder=2)
        ax.annotate("2022–26", (LATER_START, 0), xycoords=("data", "axes fraction"),
                    xytext=(4, 4), textcoords="offset points", ha="left", va="bottom",
                    fontsize=size - 1, color=colors["muted"])
        ax.set_title("LightGBM growth relative to Ridge", loc="left", color=colors["ink"],
                     fontsize=size + 1, weight="semibold", pad=12)
        ax.set_xlim(dates[0], dates[-1])
        ax.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}×"))
        ax.spines[:].set_visible(False)
        ax.grid(axis="y", color=colors["grid"], linewidth=0.5, alpha=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(colors=colors["ink"], labelsize=size - 0.5, length=0, pad=6)
        fig.subplots_adjust(left=0.13 if mobile else 0.07, right=0.97, top=0.86, bottom=0.12)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUTPUT / f"relative-growth{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=colors["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", type=Path, help="sweep_review.py output folder")
    args = parser.parse_args()
    if args.sweep:
        export(args.sweep)
    relative = json.loads((OUTPUT / "relative-growth.json").read_text())
    for dark in (False, True):
        for mobile in (False, True):
            render(relative, dark, mobile)
