"""Attribution by theme of the ranking.

Part 1: full-history return and variance share of each theme (the explorer's
no-script fallback), and each theme's return per calendar year with the block value
as a step line.
Part 2: each theme's return inside market declines and strong rallies, and
its P&L over the two deepest drawdowns.

`--outputs` reads the theme attribution folder
(projects/performance_attribution/outputs/factors-composite-*) and writes
assets/portfolio-attribution/themes.json; rendering reads only that file.
Returns are gross, in % of capital a year (mean daily contribution x 252).
A variance share is Cov(theme, gross P&L) / Var(gross P&L).
"""

from __future__ import annotations

import argparse
import math
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"
DATA = OUTPUT / "themes.json"
# Display order: the ranking's signal themes, the low-risk package (subtotal first), the rest.
SIGNALS = [
    "Short interest",
    "Short-term return",
    "Medium- and long-term return",
    "Size",
    "Trading activity",
]
LOW_RISK = ["Low-risk package", "Low volatility", "Beta", "Net market exposure"]
REST = ["Sector tilt", "Stock-specific", "Unloaded holdings"]
THEMES = (*SIGNALS, *LOW_RISK, *REST)
OVERVIEW = (*SIGNALS, "Low-risk package", *REST)
FIRST_YEAR, LAST_YEAR = 1999, 2026


def export(outputs: Path, *, data_path: Path = DATA, themes: tuple[str, ...] = THEMES) -> None:
    """Collect full-period, block and yearly values per theme from the tidy CSV."""
    out = {"full": {}, "blocks": {}, "years": {}}
    with open(outputs / "theme_periods_gross.csv") as f:
        for row in csv.DictReader(f):
            if row["theme"] == "Stock-specific (loaded holdings)":
                row["theme"] = "Stock-specific"
            if row["theme"] not in themes:
                continue
            value = [round(float(row["return_pct"]), 3), round(float(row["risk_share_pct"]), 2)]
            kind, period = row["period_type"], row["period"]
            if kind == "full":
                out["full"][row["theme"]] = value
            elif kind == "block":
                out["blocks"].setdefault(period, {})[row["theme"]] = value
            elif kind == "year":
                out["years"].setdefault(period, {})[row["theme"]] = value
    # Regimes: all decline sessions, and strong-rally sessions outside declines.
    wanted = {("overlapping", "decline"): "Declines",
              ("exclusive", "strong rally, not decline"): "Strong rallies"}
    out["regimes"] = {}
    with open(outputs / "regime_summary.csv") as f:
        for row in csv.DictReader(f):
            label = wanted.get((row["scheme"], row["regime"]))
            if label and row["leg"] == "total" and (row["theme"] in themes or row["theme"] == "Book net"):
                out["regimes"].setdefault(label, {})[row["theme"]] = round(float(row["per_year_pct"]), 2)
    out["drawdowns"] = {}
    with open(outputs / "drawdown_themes.csv") as f:
        for row in csv.DictReader(f):
            if row["leg"] == "total" and row["theme"] in themes:
                label = f"{row['peak'][:4]}\u2013{row['trough'][2:4]} drawdown"
                out["drawdowns"].setdefault(label, {})[row["theme"]] = round(float(row["pnl_pp"]), 2)
                window = [row["peak"], row["trough"]]
                if window not in out.setdefault("windows", []):
                    out["windows"].append(window)
    missing = [t for t in themes if t not in out["full"]]
    if missing:
        raise ValueError(f"themes missing from {outputs}: {missing}")
    data_path.write_text(json.dumps(out, indent=1) + "\n")


def theme_overview(aggregates: dict, *, dark: bool, mobile: bool, output: Path) -> None:
    """Use the published daily aggregates, including trading costs, for both axes."""
    c = colors(dark)
    series = {item["id"]: item for item in aggregates["series"]}
    selected = [series["total_" + key] for key in aggregates["charts"]["themes"]["series"]]
    gross = series["gross"]["values"]
    gross_mean = sum(gross) / len(gross)
    centered = [value - gross_mean for value in gross]
    gross_sum_squares = sum(value * value for value in centered)
    annual = [sum(item["values"]) / len(gross) / aggregates["scale"] * aggregates["annualization"] * 100
              for item in selected]
    risk = [sum(v * g for v, g in zip(item["values"], centered, strict=True)) / gross_sum_squares * 100
            for item in selected]
    labels = [item["label"].replace("Medium- and long-term return", "Med./long-term\nreturn") if mobile
              else item["label"] for item in selected]
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "theme-overview"}):
        fig, axes = plt.subplots(1, 2, sharey=True, figsize=(4.75, 3.6) if mobile else (8, 3.9))
        fig.set_facecolor(c["bg"])
        for axis, title, values, marker, hue in zip(axes, ("Return / year", "Risk share"), (annual, risk),
                                                    ("o", "D"), (c["pos"], c["neg"]), strict=True):
            axis.set_facecolor(c["bg"])
            axis.spines[:].set_visible(False)
            axis.set_title(title, loc="left", fontsize=10.5, color=c["ink"], pad=6)
            axis.axvline(0, color=c["muted"], lw=.7)
            axis.grid(axis="x", color=c["grid"], lw=.5)
            axis.plot(values, range(len(labels)), linestyle="none", marker=marker, color=hue, markersize=4.7)
            axis.tick_params(length=0, colors=c["ink"], labelsize=9)
            axis.xaxis.set_major_locator(plt.MaxNLocator(3))
            axis.xaxis.set_major_formatter(lambda value, _: f"{value:g}%")
            axis.margins(x=.12)
        axes[0].set_yticks(range(len(labels)), labels)
        axes[0].set_ylim(len(labels)-.4, -.6)
        fig.subplots_adjust(left=.32 if mobile else .24, right=.97, bottom=.09, top=.90, wspace=.36)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        target = output / f"theme-pnl{suffix}.svg"
        fig.savefig(target, metadata={"Date": None})
        plt.close(fig)
        target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")


def colors(dark: bool) -> dict:
    return {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4e7ea" if dark else "#25313a",
        "muted": "#9aa4ad" if dark else "#66737d",
        "grid": "#37414a" if dark else "#e2e6e9",
        "pos": "#89b5cc" if dark else "#426e89",
        "neg": "#a0acb4" if dark else "#606e77",
    }


def paired_periods(periods, rows, name, unit, *, dark, mobile, output: Path):
    """Compare the two periods on the same signed scale for each theme."""
    c = colors(dark)
    labels = [label for _, label in rows]
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": name}):
        fig, axis = plt.subplots(figsize=(4.75 if mobile else 7.4, 1.05 + 0.32 * len(rows)))
        fig.patch.set_facecolor(c["bg"])
        axis.set_facecolor(c["bg"])
        axis.spines[:].set_visible(False)
        for i, (key, _) in enumerate(rows):
            axis.plot([values[key] for _, values in periods], [i - .1, i + .1],
                      color=c["muted"], linewidth=.7, zorder=1)
        for (label, values), offset, symbol, fill, edge in zip(
            periods, (-.1, .1), ("o", "D"), (c["bg"], c["pos"]), (c["neg"], c["pos"]), strict=True
        ):
            axis.plot([values[key] for key, _ in rows], [i + offset for i in range(len(rows))],
                      linestyle="none", marker=symbol, markersize=5, markerfacecolor=fill,
                      markeredgecolor=edge, markeredgewidth=1.2, label=label)
        axis.axvline(0, color=c["muted"], linewidth=.65, zorder=0)
        axis.grid(axis="x", color=c["grid"], linewidth=.5)
        axis.set_axisbelow(True)
        axis.set_yticks(range(len(rows)), labels)
        axis.set_ylim(len(rows) - .5, -.5)
        axis.xaxis.set_major_locator(plt.MaxNLocator(4 if mobile else 6))
        axis.tick_params(length=0, colors=c["ink"], labelsize=9)
        axis.set_xlabel(unit, color=c["muted"], fontsize=9.5)
        axis.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1), ncols=2,
                    labelcolor=c["ink"], fontsize=9.5, handletextpad=.3, borderaxespad=0)
        fig.subplots_adjust(left=.37 if mobile else .27, right=.97, top=.82 if len(rows)<5 else .91,
                            bottom=.22 if len(rows)<5 else .14)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        target = output / f"{name}{suffix}.svg"
        fig.savefig(target, metadata={"Date": None}, facecolor=c["bg"])
        plt.close(fig)
        target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")


def small_multiples(data: dict, index: int, name: str, unit: str,
                    dark: bool, mobile: bool, *, themes: tuple[str, ...],
                    output: Path = OUTPUT, first_year: int = FIRST_YEAR, last_year: int = LAST_YEAR) -> None:
    """One panel per theme: yearly bars and the five-year block value as a step line.

    The common signed scale includes every annual observation.
    """
    c = colors(dark)
    cols = 1 if mobile else len(themes)
    rows = -(-len(themes) // cols)
    all_values = [values[theme][index] for values in data["years"].values() for theme in themes]
    low, high = min(0, min(all_values)), max(0, max(all_values))
    step = max(5, math.ceil((high - low) / 20) * 5)
    bottom, top = min(-step, math.floor(low / step) * step), max(step, math.ceil(high / step) * step)
    size = 10 if mobile else 10.5
    years = list(range(first_year, last_year + 1))
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": name}):
        fig, axes = plt.subplots(rows, cols, figsize=(4.75, 1.55 * rows) if mobile else (8.2, 2.1 * rows),
                                 sharex=True, sharey=True, squeeze=False)
        fig.set_facecolor(c["bg"])
        for ax in axes.flat:
            ax.set_facecolor(c["bg"])
            ax.spines[:].set_visible(False)
            ax.tick_params(length=0, colors=c["muted"], labelsize=size - 1.5)
        for ax, theme in zip(axes.flat, themes):
            values = [data["years"].get(str(y), {}).get(theme, [0, 0])[index] for y in years]
            ax.bar(years, values, width=0.75,
                   color=[c["pos"] if v >= 0 else c["neg"] for v in values])
            for period, block in data["blocks"].items():
                a, z = (int(p) for p in period.split("-"))
                ax.plot([a - 0.45, z + 0.45], [block[theme][index]] * 2, color=c["ink"],
                        linewidth=1.6, solid_capstyle="butt")
            ax.axhline(0, color=c["grid"], linewidth=0.9, zorder=0)
            ax.grid(axis="y", color=c["grid"], linewidth=0.4)
            ax.set_axisbelow(True)
            ax.set_title(theme, loc="left", color=c["ink"], fontsize=size, weight="normal", pad=4)
        for ax in axes.flat[len(themes):]:
            ax.set_visible(False)
        axes.flat[0].set_ylim(bottom - step * .06, top + step * .06)
        axes.flat[0].set_yticks([bottom, 0, top], [f"−{abs(bottom):g}", "0", f"{top:g}"])
        axes.flat[0].set_xticks([2000, 2010, 2020], ["2000", "2010", "2020"])
        for ax in axes.flat:
            ax.tick_params(labelbottom=True)
        fig.text(0.01, 0.995, unit, ha="left", va="top", color=c["muted"], fontsize=size - 1)
        fig.subplots_adjust(left=0.09 if mobile else 0.05, right=0.99, top=0.95 if mobile else 0.76,
                            bottom=0.05 if mobile else 0.17, hspace=0.75, wspace=0.12)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = output / f"{name}{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=c["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, help="theme attribution output folder")
    args = parser.parse_args()
    if args.outputs:
        export(args.outputs)
    data = json.loads(DATA.read_text())
    aggregates = json.loads((OUTPUT / "interactive-themes.json").read_text())
    overview_order = [(t, t) for t in OVERVIEW]
    for dark in (False, True):
        for mobile in (False, True):
            theme_overview(aggregates, dark=dark, mobile=mobile, output=OUTPUT)
            small_multiples(data, 0, "theme-return-years", "Gross return (% per year)", dark, mobile,
                            themes=("Short-term return", "Short interest"))
            regime_rows = [(key, key if i == 0 else "↳ " + key) for i, key in enumerate(LOW_RISK)]
            paired_periods([(key, data["regimes"][key]) for key in ("Declines", "Strong rallies")],
                           regime_rows, "theme-regimes", "Return (% of capital per year)",
                           dark=dark, mobile=mobile, output=OUTPUT)
            paired_periods([(key.removesuffix(" drawdown"), values) for key, values in sorted(data["drawdowns"].items())],
                           overview_order, "theme-drawdowns", "P&L (points of capital)",
                           dark=dark, mobile=mobile, output=OUTPUT)
