"""Figures for the Ridge style-removal article.

Reads the staged aggregates in data/ridge_style_removal_blog_20261026 (see its README) and writes
static light/dark/mobile SVGs plus the interactive cumulative-gap chart into assets/ridge-style-removal.
Statistics are computed per rebalance calendar and then averaged; only portfolio aggregates are exported.
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import polars as pl
from blog_charts import series, write_chart

DATA = Path("/Users/pjinghelbrecht/ResearchLocal/quant_research/data/ridge_style_removal_blog_20261026")
SPLIT_YEAR = 2019
STRENGTHS = (("none", 0), ("style25", 25), ("style50", 50), ("style75", 75), ("style100", 100))
PCA = (("pca25", 25), ("pca50", 50))


def palette(dark: bool) -> dict[str, str]:
    return {"bg": "#0d1117" if dark else "#ffffff", "ink": "#e4e7ea" if dark else "#25313a",
            "muted": "#9ba5af" if dark else "#59636e", "grid": "#37414a" if dark else "#e2e6e9",
            "base": "#6e7681" if dark else "#a3acb5", "style": "#3987e5" if dark else "#2a78d6",
            "style50": "#a8891a" if dark else "#b58900", "pca": "#2aa3c4" if dark else "#0e8fad",
            "other": "#4b565f" if dark else "#d3d9de"}


def sharpe(frame: pl.DataFrame, arm: str) -> float:
    """Net Sharpe per calendar, averaged over the three calendars."""
    return sum(frame[f"{arm}_o{k}"].mean() / frame[f"{arm}_o{k}"].std() * 252 ** .5 for k in range(3)) / 3


def returns() -> pl.DataFrame:
    return pl.read_parquet(DATA / "derived/daily_net_returns.parquet")


def save(fig, path: Path, c: dict) -> None:
    fig.savefig(path, metadata={"Date": None}, facecolor=c["bg"], bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


def style(ax, c: dict, mobile: bool, grid: str = "y") -> None:
    ax.set_facecolor(c["bg"])
    ax.tick_params(length=0, colors=c["muted"], labelsize=10 if mobile else 10.5)
    ax.grid(axis=grid, color=c["grid"], lw=0.8)
    ax.set_axisbelow(True)
    for side in ax.spines.values():
        side.set_visible(False)


def suffix(dark: bool, mobile: bool) -> str:
    return ("_mobile" if mobile else "") + ("_dark" if dark else "")


def box(ax, c, x, y, w, h, text, kind="plain", size=10.0):
    """Rounded box with centred text; kind picks the accent colour."""
    from matplotlib.patches import FancyBboxPatch
    edge = {"plain": c["muted"], "dial": c["style"], "style": c["style"], "specific": c["base"]}[kind]
    fill = {"plain": c["bg"], "dial": c["style"], "style": c["bg"], "specific": c["bg"]}[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08", fc=fill, ec=edge,
                                lw=1.3, alpha=1.0 if kind != "dial" else 0.92, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, zorder=3,
            color="#ffffff" if kind == "dial" else c["ink"], linespacing=1.25)


def arrow(ax, c, start, end, color=None, ls="-", rad=0.0):
    ax.annotate("", xy=end, xytext=start, zorder=1, arrowprops=dict(
        arrowstyle="-|>", color=color or c["muted"], lw=1.3, ls=ls, shrinkA=0, shrinkB=0,
        mutation_scale=11, connectionstyle=f"arc3,rad={rad}"))


def render_diagram(out: Path, dark: bool, mobile: bool) -> None:
    c = palette(dark)
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-diagram"}):
        if mobile:
            fig, ax = plt.subplots(figsize=(4.4, 7.4)); ax.set_xlim(0, 4.4); ax.set_ylim(0, 7.4)
            w, h, x0 = 3.5, 0.62, 0.45
            steps = [("Ridge forecast", "plain"), ("Fit sectors and six styles,\neach date", "plain"),
                     ("Subtract \u03bb \u00d7 style part", "dial"), ("Select 75 long, 75 short", "plain"),
                     ("Size to the 7% volatility target", "plain"), ("Book weights w", "plain")]
            ys = [6.55 - i * 0.92 for i in range(len(steps))]
            for (text, kind), y in zip(steps, ys):
                box(ax, c, x0, y, w, h, text, kind, 9.5)
            for upper, lower in zip(ys, ys[1:]):
                arrow(ax, c, (x0 + w / 2, upper), (x0 + w / 2, lower + h))
            ax.text(0.0, 7.3, "Input: the forecast", fontsize=9.5, color=c["muted"], va="center")
            ax.text(0.0, 1.75, "Output: the book's P&L", fontsize=9.5, color=c["muted"], va="center")
            gy = 0.15
            box(ax, c, 0.05, gy, 2.05, 0.95, "Style P&L\nand variance\n(exposure X\u2032w)", "style", 9.2)
            box(ax, c, 2.3, gy, 2.05, 0.95, "Stock-specific\nP&L and variance\n(w\u2032e)", "specific", 9.2)
            arrow(ax, c, (x0 + w / 2, ys[-1]), (x0 + w / 2, gy + 1.15))
            ax.plot([1.075, 3.325], [gy + 1.15, gy + 1.15], color=c["muted"], lw=1.3)
            arrow(ax, c, (1.075, gy + 1.15), (1.075, gy + 0.95)); arrow(ax, c, (3.325, gy + 1.15), (3.325, gy + 0.95))
        else:
            fig, ax = plt.subplots(figsize=(9.4, 4.5)); ax.set_xlim(0, 9.4); ax.set_ylim(0, 4.5)
            w, h = 1.36, 1.0
            xs = [0.0, 1.608, 3.216, 4.824, 6.432, 8.04]
            steps = [("Ridge\nforecast", "plain"), ("Fit sectors and\nsix styles,\neach date", "plain"),
                     ("Subtract\n\u03bb \u00d7 style part", "dial"), ("Select 75 long\nand 75 short\nnames", "plain"),
                     ("Size to the 7%\nvolatility\ntarget", "plain"), ("Book\nweights w", "plain")]
            y = 3.2
            ax.text(0.0, 4.4, "Input: what the forecast hands the portfolio", fontsize=10.5, color=c["muted"], va="center")
            for (text, kind), x in zip(steps, xs):
                box(ax, c, x, y, w, h, text, kind, 9.6)
            for x in xs[:-1]:
                arrow(ax, c, (x + w + 0.02, y + h / 2), (x + 1.608 - 0.02, y + h / 2))
            gy = 0.3
            ax.text(0.0, gy + 0.5, "Output: attribution\nof the book's P&L\nand variance", fontsize=10.5,
                    color=c["muted"], va="center", linespacing=1.3)
            box(ax, c, 2.5, gy, 2.9, 0.95, "Style P&L and variance\nfrom the exposure X\u2032w", "style", 10)
            box(ax, c, 5.9, gy, 2.9, 0.95, "Stock-specific P&L and\nvariance from w\u2032e", "specific", 10)
            fx = xs[-1] + w / 2
            arrow(ax, c, (fx, y), (fx, 2.1)); ax.plot([4.95, fx], [2.1, 2.1], color=c["muted"], lw=1.3)
            ax.plot([7.35, 7.35], [2.1, 1.25], color=c["muted"], lw=1.3)
            arrow(ax, c, (4.95, 2.1), (4.95, gy + 0.95)); arrow(ax, c, (7.35, 2.1), (7.35, gy + 0.95))
            arrow(ax, c, (xs[2] + w / 2, y), (3.45, gy + 0.95), color=c["style"], ls=(0, (3, 2)))
            ax.text(3.38, 2.2, "\u03bb moves\nthis", fontsize=9.5, color=c["style"], ha="right", va="center", linespacing=1.2)
        ax.axis("off")
        fig.set_facecolor(c["bg"])
        save(fig, out / f"removal-diagram{suffix(dark, mobile)}.svg", c)


def render_shares(out: Path, dark: bool, mobile: bool) -> None:
    c = palette(dark)
    shares = (pl.read_csv(DATA / "inputs/q1_variance_shares_by_year.csv").filter(pl.col("model") == "ridge")
              .sort("year").with_columns(other=pl.col("sh_sec") + pl.col("sh_cross")))
    years = shares["year"].to_list()
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-shares"}):
        fig, ax = plt.subplots(figsize=(4.4, 3.6) if mobile else (9.4, 3.5))
        fig.set_facecolor(c["bg"]); style(ax, c, mobile)
        ax.stackplot(years, shares["sh_style"] * 100, shares["sh_resid"] * 100, shares["other"] * 100,
                     colors=[c["style"], c["base"], c["other"]], alpha=0.9, lw=0)
        ax.set_xlim(years[0], years[-1]); ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
        ax.set_xticks([1999, 2005, 2010, 2015, 2020, 2025] if not mobile else [1999, 2010, 2020])
        for text, x, y, colour in (("Style", 2013, 22, "#ffffff"), ("Stock-specific", 2013, 72, c["ink"])):
            ax.text(x, y, text, ha="center", va="center", fontsize=10.5, color=colour)
        ax.set_title("Share of forecast cross-sectional variance", loc="left", fontsize=11, color=c["ink"], pad=10)
        save(fig, out / f"forecast-style-share{suffix(dark, mobile)}.svg", c)


def render_variance(out: Path, dark: bool, mobile: bool) -> None:
    """Realized variance of the book by share of style removed, split into factor and non-factor parts."""
    c = palette(dark)
    order = ["P0", "P25", "P50", "P75", "P100"]
    rows = {r["arm"]: r for r in pl.read_csv(DATA / "inputs/q2_excess_variance.csv").iter_rows(named=True)}
    labels = ["None", "25%", "50%", "75%", "100%"]
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-variance"}):
        fig, ax = plt.subplots(figsize=(4.4, 3.5) if mobile else (6.8, 3.4))
        fig.set_facecolor(c["bg"]); style(ax, c, mobile)
        for i, arm in enumerate(order):
            factor, rest = rows[arm]["ols_factor_var"], rows[arm]["ols_resid_var"]
            ax.bar(i, factor, 0.62, color=c["style"], zorder=2)
            ax.bar(i, rest, 0.62, bottom=factor, color=c["base"], zorder=2)
            ax.text(i, factor / 2, f"{factor:.0f}", ha="center", va="center", fontsize=10, color="#ffffff", zorder=3)
            ax.text(i, factor + rest / 2, f"{rest:.0f}", ha="center", va="center", fontsize=10, color=c["ink"] if dark else "#25313a", zorder=3)
            ax.text(i, factor + rest + 1.5, f"{rows[arm]['net_vol']:.1f}% vol.", ha="center", va="bottom", fontsize=9.5, color=c["muted"])
        ax.set_xticks(range(5), labels); ax.set_ylim(0, 95); ax.set_yticks([0, 20, 40, 60, 80])
        ax.set_xlim(-0.5, 4.5)
        ax.set_title("Realized variance (%\u00b2 a year) by share of style removed", loc="left", fontsize=11, color=c["ink"], pad=10)
        save(fig, out / f"variance-split{suffix(dark, mobile)}.svg", c)


def curve_points(frame: pl.DataFrame) -> dict[str, dict[str, float]]:
    early = frame.filter(pl.col("date").dt.year() < SPLIT_YEAR)
    late = frame.filter(pl.col("date").dt.year() >= SPLIT_YEAR)
    return {arm: {"early": sharpe(early, arm), "late": sharpe(late, arm)} for arm, _ in STRENGTHS + PCA}


def render_curve(out: Path, dark: bool, mobile: bool) -> None:
    c = palette(dark)
    points = curve_points(returns())
    xs = [x for _, x in STRENGTHS]
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-curve"}):
        fig, ax = plt.subplots(figsize=(4.4, 3.8) if mobile else (8.2, 3.7))
        fig.set_facecolor(c["bg"]); style(ax, c, mobile)
        for key, colour in (("early", c["style"]), ("late", c["style50"])):
            ax.plot(xs, [points[arm][key] for arm, _ in STRENGTHS], color=colour, lw=2.0, marker="o", ms=5.5, zorder=3)
            ax.plot([x for _, x in PCA], [points[arm][key] for arm, _ in PCA], ls="none", marker="D", ms=6.5,
                    mfc=c["bg"], mec=c["pca"], mew=1.6, zorder=4)
        ax.text(104, points["style100"]["early"], "1999–2018", va="center", fontsize=10.5, color=c["style"])
        ax.text(104, points["style100"]["late"], "2019–2026", va="center", fontsize=10.5, color=c["style50"])
        ax.text(52, points["pca50"]["early"] - 0.09, "PCA, 10 factors", ha="center", va="top", fontsize=9.5, color=c["pca"])
        ax.set_xlim(-3, 128 if not mobile else 140); ax.set_xticks(xs, ["None", "25%", "50%", "75%", "100%"])
        ax.set_ylim(0.3, 1.85); ax.set_yticks([0.4, 0.8, 1.2, 1.6])
        ax.set_title("Net Sharpe ratio by share of style removed", loc="left", fontsize=11, color=c["ink"], pad=10)
        save(fig, out / f"strength-curve{suffix(dark, mobile)}.svg", c)


ARMS_SHOWN = (("style25", "Style 25%", "long", "style"), ("style50", "Style 50%", "size", "style50"))


def gap_series() -> tuple[list[str], list[dict]]:
    """Daily difference against no removal, mean of three calendars, anchored at zero the day before."""
    frame = returns().sort("date")
    first = (frame["date"][0] - dt.timedelta(days=1)).isoformat()
    dates = [first, *[d.isoformat() for d in frame["date"]]]
    data = []
    for arm, label, role, _ in ARMS_SHOWN:
        diff = sum(frame[f"{arm}_o{k}"] - frame[f"none_o{k}"] for k in range(3)) / 3
        data.append(series(arm, label, role, [0.0, *diff.to_list()], additive=True, drawdown=False))
    return dates, data


def export_gap_chart(assets: Path) -> None:
    dates, data = gap_series()
    write_chart(assets / "cumulative-gap.json", dates, data, {"gap": dict(
        kind="performance", series=[s["id"] for s in data], additive=True,
        unit="Cumulative net return vs no removal (points)", statistics=False, zeroReference=True,
        showWindow=False, dateLabelSpacing=10,
        dateTicks=[dates[0], "2005-01-01", "2010-01-01", "2015-01-01", "2020-01-01", dates[-1]],
        mobileDateTicks=[dates[0], "2005-01-01", "2015-01-01", dates[-1]],
        start=dates[0], marker=f"{SPLIT_YEAR}-01-01", shade=[[f"{SPLIT_YEAR}-01-01", dates[-1]]],
        episodes=[["1999–2018", dates[0], "2018-12-31"], ["2019–2026", "2018-12-31", dates[-1]]],
        note="Sum of daily net return differences against no removal, mean of three rebalance calendars, points of capital. Shaded: 2019 onward.")})


def render_gap(out: Path, dark: bool, mobile: bool) -> None:
    c = palette(dark)
    dates, data = gap_series()
    x = [dt.date.fromisoformat(d) for d in dates]
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-gap"}):
        fig, ax = plt.subplots(figsize=(4.4, 4.0) if mobile else (9.4, 3.9))
        fig.set_facecolor(c["bg"]); style(ax, c, mobile)
        ax.axhline(0, color=c["ink"], lw=0.8)
        ax.axvspan(dt.date(SPLIT_YEAR, 1, 1), x[-1], color=c["grid"], alpha=0.55, zorder=0)
        cumulative = {}
        for (arm, label, _, colour), s in zip(ARMS_SHOWN, data):
            values = [0.0]
            for v in s["values"][1:]:
                values.append(values[-1] + v / 1e10 * 100)
            cumulative[arm] = values
            ax.plot(x, values, color=c[colour], lw=1.7)
            ax.text(x[-1] + dt.timedelta(days=150), values[-1], label, va="center", fontsize=10, color=c[colour])
        ax.set_xlim(x[0], x[-1] + dt.timedelta(days=(900 if mobile else 1000)))
        ticks = (2005, 2015) if mobile else (2005, 2010, 2015, 2020)
        ax.set_xticks([x[0], *[dt.date(y, 1, 1) for y in ticks]], [str(x[0].year), *map(str, ticks)])
        ax.set_title("Cumulative net return vs no removal (points of capital)", loc="left", fontsize=11, color=c["ink"], pad=10)
        save(fig, out / f"cumulative-gap{suffix(dark, mobile)}.svg", c)


def export(assets: Path) -> None:
    assets.mkdir(parents=True, exist_ok=True)
    export_gap_chart(assets)
    for dark in (False, True):
        for mobile in (False, True):
            for render in (render_diagram, render_shares, render_variance, render_curve, render_gap):
                render(assets, dark, mobile)


if __name__ == "__main__":
    export(Path(__file__).resolve().parents[1] / "assets/ridge-style-removal")
