"""Attribution by theme of the ranking.

Part 1, Figure A: full-history return and variance share of each theme.
Part 1, Figures B and C: each theme's return and variance share per calendar
year, with the five-year block value as a step line.
Part 2: each theme's return inside market declines and strong rallies, and
its P&L over the two deepest drawdowns.

`--outputs` reads the theme attribution folder
(projects/performance_attribution/outputs/theme-over-time-*) and writes
assets/portfolio-attribution/themes.json; rendering reads only that file.
Returns are gross, in % of capital a year (mean daily contribution x 252).
A variance share is Cov(theme, gross P&L) / Var(gross P&L).
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"
DATA = OUTPUT / "themes.json"
# Display order: the ranking's signal themes, then the defensive themes, then the rest.
THEMES = [
    "Short interest",
    "Momentum",
    "Trend",
    "Short-term reversal",
    "Price position",
    "Loss frequency",
    "Liquidity & volume",
    "Low volatility",
    "Size",
    "Beta & market correlation",
    "Net market exposure",
    "Sector tilt",
    "Stock-specific",
]
FIRST_YEAR, LAST_YEAR = 1999, 2026


def export(outputs: Path) -> None:
    """Collect full-period, block and yearly values per theme from the tidy CSV."""
    out = {"full": {}, "blocks": {}, "years": {}}
    with open(outputs / "theme_periods_gross.csv") as f:
        for row in csv.DictReader(f):
            if row["theme"] not in THEMES:
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
            if label and row["leg"] == "total" and (row["theme"] in THEMES or row["theme"] == "Book net"):
                out["regimes"].setdefault(label, {})[row["theme"]] = round(float(row["per_year_pct"]), 2)
    out["drawdowns"] = {}
    with open(outputs / "drawdown_themes.csv") as f:
        for row in csv.DictReader(f):
            if row["leg"] == "total" and row["theme"] in THEMES:
                label = f"{row['peak'][:4]}\u2013{row['trough'][2:4]} drawdown"
                out["drawdowns"].setdefault(label, {})[row["theme"]] = round(float(row["pnl_pp"]), 2)
                window = [row["peak"], row["trough"]]
                if window not in out.setdefault("windows", []):
                    out["windows"].append(window)
    missing = [t for t in THEMES if t not in out["full"]]
    if missing:
        raise ValueError(f"themes missing from {outputs}: {missing}")
    DATA.write_text(json.dumps(out, indent=1) + "\n")


def render(panels: list[tuple[str, dict, str]], name: str, dark: bool, mobile: bool,
           shared_scale: bool = False, row_order: list = (), wrap_labels: bool = False) -> None:
    """Draw one horizontal bar panel per (title, {key: value}, format).

    `row_order` lists (key, label) rows top to bottom; None adds a half-row gap.
    `wrap_labels` breaks long labels after their first word on phones and leaves
    more room for them on desktop.
    """
    colors = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4e7ea" if dark else "#25313a",
        "grid": "#37414a" if dark else "#e2e6e9",
        "pos": "#6ab8aa" if dark else "#287d70",
        "neg": "#e5a081" if dark else "#b86642",
    }
    size = 10.5 if mobile else 11
    rows, y, positions = [], 0.0, []
    for row in row_order:
        if row is None:
            y += 0.5
            continue
        rows.append(row)
        positions.append(y)
        y += 1
    with plt.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "svg.hashsalt": "attribution-components",
        }
    ):
        fig, axes = plt.subplots(
            1, 2, figsize=(5, 6.4) if mobile else (9, 5.6), sharey=True,
            gridspec_kw={"wspace": 0.55 if mobile else 0.45},
        )
        fig.set_facecolor(colors["bg"])
        every = [values[k] for _, values, _ in panels for k, _ in rows]
        for ax, (title, values, fmt) in zip(axes, panels, strict=True):
            data = [values[k] for k, _ in rows]
            limits = every if shared_scale else data
            ax.set_facecolor(colors["bg"])
            ax.barh(positions, data, height=0.62,
                    color=[colors["pos"] if v >= 0 else colors["neg"] for v in data])
            span = max(abs(v) for v in limits)
            for p, v in zip(positions, data, strict=True):
                ax.annotate(fmt.format(v if abs(v) >= 0.05 else 0.0).replace("-", "\u2212"), (max(v, 0), p), xytext=(4, 0), textcoords="offset points",
                            va="center", ha="left", fontsize=size - 1, color=colors["ink"])
            # Room for the value labels beside the longest bar.
            ax.set_xlim(min(min(limits), 0) - 0.05 * span, span * (1.7 if mobile else 1.35))
            ax.axvline(0, color=colors["grid"], linewidth=0.9)
            ax.set_title(title, loc="left", color=colors["ink"], fontsize=size + 0.5,
                         weight="semibold", pad=10)
            ax.spines[:].set_visible(False)
            ax.tick_params(axis="x", length=0, colors=colors["ink"], labelsize=size - 1)
            ax.tick_params(axis="y", length=0, colors=colors["ink"], labelsize=size)
            ax.xaxis.set_major_locator(plt.MaxNLocator(3))
            ax.grid(axis="x", color=colors["grid"], linewidth=0.5)
            ax.set_axisbelow(True)
        labels = [label.replace(" ", "\n", 1) if wrap_labels and mobile and len(label) > 15
                  else label for _, label in rows]
        axes[0].set_yticks(positions, labels)
        axes[0].invert_yaxis()
        left = 0.32 if mobile else (0.2 if wrap_labels else 0.17)
        fig.subplots_adjust(left=left, right=0.97, top=0.92, bottom=0.06)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUTPUT / f"{name}{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=colors["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


def colors(dark: bool) -> dict:
    return {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4e7ea" if dark else "#25313a",
        "muted": "#9aa4ad" if dark else "#66737d",
        "grid": "#37414a" if dark else "#e2e6e9",
        "pos": "#6ab8aa" if dark else "#287d70",
        "neg": "#e5a081" if dark else "#b86642",
    }


def small_multiples(data: dict, index: int, name: str, limit: float, unit: str,
                    dark: bool, mobile: bool) -> None:
    """One panel per theme: yearly bars and the five-year block value as a step line.

    All panels share the y-scale [-limit, limit]; bars beyond it are clipped and
    marked with a small caret so no panel hides a large value.
    """
    c = colors(dark)
    cols = 2 if mobile else 4
    rows = -(-len(THEMES) // cols)
    size = 10 if mobile else 10.5
    years = list(range(FIRST_YEAR, LAST_YEAR + 1))
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": name}):
        fig, axes = plt.subplots(rows, cols, figsize=(5.2, 1.55 * rows) if mobile else (10, 1.7 * rows),
                                 sharex=True, sharey=True)
        fig.set_facecolor(c["bg"])
        for ax in axes.flat:
            ax.set_facecolor(c["bg"])
            ax.spines[:].set_visible(False)
            ax.tick_params(length=0, colors=c["muted"], labelsize=size - 1.5)
        for ax, theme in zip(axes.flat, THEMES):
            values = [data["years"].get(str(y), {}).get(theme, [0, 0])[index] for y in years]
            shown = [max(-limit, min(limit, v)) for v in values]
            ax.bar(years, shown, width=0.75,
                   color=[c["pos"] if v >= 0 else c["neg"] for v in values])
            for y, v in zip(years, values):
                if abs(v) > limit:
                    ax.annotate("▲" if v > 0 else "▼", (y, limit if v > 0 else -limit),
                                ha="center", va="bottom" if v > 0 else "top", fontsize=6,
                                color=c["pos"] if v > 0 else c["neg"])
            for period, block in data["blocks"].items():
                a, z = (int(p) for p in period.split("-"))
                ax.plot([a - 0.45, z + 0.45], [block[theme][index]] * 2, color=c["ink"],
                        linewidth=1.6, solid_capstyle="butt")
            ax.axhline(0, color=c["grid"], linewidth=0.9, zorder=0)
            ax.grid(axis="y", color=c["grid"], linewidth=0.4)
            ax.set_axisbelow(True)
            ax.set_title(theme, loc="left", color=c["ink"], fontsize=size, weight="semibold", pad=4)
        for ax in axes.flat[len(THEMES):]:
            ax.set_visible(False)
        axes.flat[0].set_ylim(-limit * 1.12, limit * 1.12)
        axes.flat[0].set_yticks([-limit, 0, limit],
                                [f"−{limit:g}", "0", f"+{limit:g}"])
        axes.flat[0].set_xticks([2000, 2010, 2020], ["2000", "2010", "2020"])
        for ax in axes.flat:
            ax.tick_params(labelbottom=True)
        fig.text(0.01, 0.995, unit, ha="left", va="top", color=c["muted"], fontsize=size - 1)
        fig.subplots_adjust(left=0.09 if mobile else 0.05, right=0.99, top=0.95 if mobile else 0.93,
                            bottom=0.04 if mobile else 0.06, hspace=0.75, wspace=0.12)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUTPUT / f"{name}{suffix}.svg"
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
    full = [
        ("Return (% a year)", {t: data["full"][t][0] for t in THEMES}, "{:+.1f}"),
        ("Share of risk (%)", {t: data["full"][t][1] for t in THEMES}, "{:.1f}"),
    ]
    order = [(t, t) for t in THEMES[:7]] + [None] + [(t, t) for t in THEMES[7:11]] + [None] \
        + [(t, t) for t in THEMES[11:]]
    for dark in (False, True):
        for mobile in (False, True):
            render(full, "theme-pnl", dark, mobile, row_order=order, wrap_labels=True)
            small_multiples(data, 0, "theme-return-years", 10, "Return, % a year", dark, mobile)
            small_multiples(data, 1, "theme-risk-years", 40, "Share of risk, %", dark, mobile)
            regimes = [(f"{k} (% a year)", v, "{:+.1f}") for k, v in data["regimes"].items()]
            render(regimes, "theme-regimes", dark, mobile, shared_scale=True,
                   row_order=[("Book net", "Whole book, net"), None] + order, wrap_labels=True)
            drawdowns = sorted(data["drawdowns"].items())
            render([(f"{k} (points)", v, "{:+.1f}") for k, v in drawdowns], "theme-drawdowns",
                   dark, mobile, shared_scale=True, row_order=order, wrap_labels=True)
