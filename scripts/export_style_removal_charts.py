"""Figures for the Ridge style-removal article.

Reads the evidence of projects/ridge_style_removal (see its README) and writes
static light/dark/mobile SVGs plus the interactive cumulative-gap chart into assets/ridge-style-removal.
Statistics are computed per rebalance calendar and then averaged; only portfolio aggregates are exported.
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
from dataclasses import dataclass
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import polars as pl
from blog_charts import series, write_chart

DATA = Path("/Users/pjinghelbrecht/ResearchLocal/quant_research/projects/ridge_style_removal")
SPLIT_YEAR = 2019
STRENGTHS = (("none", 0), ("style25", 25), ("style50", 50), ("style75", 75), ("style100", 100))
PCA = (("pca25", 25), ("pca50", 50))


# (arm, label, interactive role, static colour, dash).
ARMS_SHOWN = (("style25", "Style 25%", "long", "style", "solid"), ("style50", "Style 50%", "size", "style50", "solid"),
              ("pca50", "PCA 50%", "cash", "pca", "solid"))


@dataclass(frozen=True)
class StyleRemovalFigures:
    data: Path = DATA
    split_year: int = SPLIT_YEAR
    arms: tuple[tuple[str, str, str, str, str], ...] = ARMS_SHOWN


def palette(dark: bool) -> dict[str, str]:
    return {"bg": "#0d1117" if dark else "#ffffff", "ink": "#e4e7ea" if dark else "#25313a",
            "muted": "#9ba5af" if dark else "#59636e", "grid": "#37414a" if dark else "#e2e6e9",
            "base": "#6e7681" if dark else "#a3acb5", "style": "#3987e5" if dark else "#2a78d6", "si": "#9085e9" if dark else "#7447c9",
            "style50": "#a8891a" if dark else "#b58900", "pca": "#2aa3c4" if dark else "#0e8fad",
            "other": "#4b565f" if dark else "#d3d9de"}


def sharpe(frame: pl.DataFrame, arm: str) -> float:
    """Net Sharpe per calendar, averaged over the three calendars."""
    return sum(frame[f"{arm}_o{k}"].mean() / frame[f"{arm}_o{k}"].std() * 252 ** .5 for k in range(3)) / 3


def returns(data: Path) -> pl.DataFrame:
    return pl.read_parquet(data / "outputs/evidence/daily_net_returns.parquet")


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


def render_diagram(out: Path, dark: bool, mobile: bool) -> None:
    """The one operation that differs between the original and adjusted book."""
    c = palette(dark)
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "svg.hashsalt": "style-removal-diagram"}):
        fig, ax = plt.subplots(figsize=(4.6, .95) if mobile else (7.8, .85))
        fig.set_facecolor(c["bg"])
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis("off")
        stages = [(0.09, "Ridge\nscore"), (.50, "Subtract λ × fitted\nstyle contribution"),
                  (.91, "Portfolio\noptimizer")]
        for x, label in stages:
            ax.text(x, .5, label, ha="center", va="center", color=c["ink"],
                    fontsize=10 if mobile else 11, linespacing=1.3)
        for start, end in ((.19, .28), (.72, .8)):
            ax.annotate("", xy=(end, .5), xytext=(start, .5),
                        arrowprops={"arrowstyle": "->", "color": c["muted"], "lw": .9})
        fig.subplots_adjust(left=.02, right=.98, bottom=.08, top=.92)
        save(fig, out / f"removal-diagram{suffix(dark, mobile)}.svg", c)


def render_shares(out: Path, dark: bool, mobile: bool, data: Path) -> None:
    """Track each part of the variance on a common 0–100% scale."""
    c = palette(dark)
    shares = (pl.read_csv(data / "inputs/q1_variance_shares_by_year.csv")
              .filter(pl.col("model") == "ridge").sort("year")
              .with_columns(other=pl.col("sh_sec") + pl.col("sh_cross")))
    years = shares["year"].to_list()
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "svg.hashsalt": "style-removal-shares"}):
        fig, ax = plt.subplots(figsize=(4.75, 2.45) if mobile else (8.0, 2.8))
        fig.set_facecolor(c["bg"])
        style(ax, c, mobile)
        ax.set(ylim=(0, 100), xlim=(years[0], years[-1]))
        ax.set_yticks((0, 50, 100), ("0%", "50%", "100%"))
        ax.set_xticks((2000, 2010, 2020) if mobile else (2000, 2005, 2010, 2015, 2020, 2025))
        lines = [("sh_style", "Styles", "#89b5cc" if dark else "#426e89", "-"),
                 ("sh_resid", "Stock-specific", c["muted"], "--"),
                 ("other", "Sector + overlap", c["muted"], ":")]
        for column, label, color, pattern in lines:
            values = shares[column].to_numpy() * 100
            ax.plot(years, values, ls=pattern, lw=1.9 if column == "sh_style" else 1.35, color=color)
            ax.annotate(label, xy=(years[-1], values[-1]), xytext=(5, 0),
                        textcoords="offset points", va="center", color=color, fontsize=9.5)
        fig.subplots_adjust(left=.1, right=.70 if mobile else .82, top=.95, bottom=.17)
        save(fig, out / f"forecast-style-share{suffix(dark, mobile)}.svg", c)


def render_risk_return(out: Path, dark: bool, mobile: bool, data: Path) -> None:
    """Realized volatility and net Sharpe ratio for every variant, mean of three schedules."""
    c = palette(dark)
    m = {r["arm"]: r for r in pl.read_csv(data / "outputs/evidence/table_metrics.csv").iter_rows(named=True)}
    rows = [("none", "No removal", "base"), ("style25", "Style 25%", "style"), ("style50", "Style 50%", "style"),
            ("style75", "Style 75%", "style"), ("style100", "Style 100%", "style"),
            ("pca25", "PCA 25%", "pca"), ("pca50", "PCA 50%", "pca")]
    ys = list(range(len(rows)))[::-1]
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-risk-return"}):
        if mobile:
            fig, axes = plt.subplots(2, 1, figsize=(4.4, 7.6), gridspec_kw={"hspace": 0.4})
        else:
            fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.2), sharey=True, gridspec_kw={"wspace": 0.1})
        fig.set_facecolor(c["bg"])
        panels = (("Volatility (% a year)", "vol_pct", (6.8, 9.4), [7, 8, 9], "{:.1f}"),
                  ("Net Sharpe ratio", "net_sharpe", (1.1, 1.58), [1.1, 1.2, 1.3, 1.4, 1.5], "{:.2f}"))
        for k, (ax, (title, col, lim, ticks, fmt)) in enumerate(zip(axes, panels)):
            style(ax, c, mobile, grid="x")
            ax.axvline(m["none"][col], color=c["muted"], lw=0.8, ls=(0, (2, 3)), zorder=1)
            for y, (arm, label, colour) in zip(ys, rows):
                v = m[arm][col]
                ax.plot([m["none"][col], v], [y, y], color=c[colour], lw=1.4, alpha=0.5, zorder=2)
                ax.plot(v, y, "o", ms=7, color=c[colour], zorder=3)
                left = v < m["none"][col] - 1e-9
                off = (lim[1] - lim[0]) * 0.025
                ax.text(v - off if left else v + off, y, fmt.format(v), va="center", ha="right" if left else "left",
                        fontsize=9, color=c["ink"])
            ax.set_xlim(*lim); ax.set_xticks(ticks)
            ax.set_title(title, loc="left", fontsize=10.5, color=c["ink"], pad=8)
            if k == 0 or mobile:
                ax.set_yticks(ys, [r[1] for r in rows])
                for tick in ax.get_yticklabels():
                    tick.set_color(c["ink"])
            else:
                ax.tick_params(axis="y", labelleft=False)
        save(fig, out / f"risk-return{suffix(dark, mobile)}.svg", c)


def render_deltas(out: Path, dark: bool, mobile: bool, data: Path) -> None:
    """Net Sharpe difference against no removal by strength, with paired block-bootstrap intervals, before and from 2019."""
    c = palette(dark)
    intervals = pl.read_csv(data / "outputs/evidence/delta_sharpe_intervals.csv").filter(pl.col("base") == "none")
    table = {(r["arm"], r["period"]): r for r in intervals.iter_rows(named=True)}
    periods = (("early", "1999\u20132018"), ("late", "2019\u20132026"))
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-deltas"}):
        fig, axes = plt.subplots(2, 1, figsize=(4.4, 5.8), sharey=True, gridspec_kw={"hspace": 0.45}) if mobile else \
            plt.subplots(1, 2, figsize=(9.4, 3.5), sharey=True, gridspec_kw={"wspace": 0.08})
        fig.set_facecolor(c["bg"])
        strengths = (("style25", 0), ("style50", 1), ("style75", 2), ("style100", 3))
        pca = (("pca25", 0), ("pca50", 1))
        for ax, (key, title) in zip(axes, periods):
            style(ax, c, mobile)
            ax.axhline(0, color=c["ink"], lw=0.8, zorder=1)
            for arm, x in strengths:
                r = table[(arm, key)]
                ax.vlines(x, r["lo"], r["hi"], color=c["style"], lw=2.2, zorder=2)
                ax.plot(x, r["delta"], "o", ms=7, color=c["style"], zorder=3)
            for arm, x in pca:
                r = table[(arm, key)]
                ax.vlines(x + 0.22, r["lo"], r["hi"], color=c["pca"], lw=1.6, zorder=2)
                ax.plot(x + 0.22, r["delta"], "D", ms=6, mfc=c["bg"], mec=c["pca"], mew=1.5, zorder=3)
            ax.set_xlim(-0.5, 3.5); ax.set_xticks(range(4), ["25%", "50%", "75%", "100%"])
            ax.set_ylim(-1.45, 0.85); ax.set_yticks([-1.0, -0.5, 0, 0.5])
            ax.set_title(title, loc="left", fontsize=11, color=c["ink"], pad=8)
        axes[0].text(0.22, table[("pca25", "early")]["lo"] - 0.07, "PCA", ha="center", va="top", fontsize=9.5, color=c["pca"])
        save(fig, out / f"delta-sharpe{suffix(dark, mobile)}.svg", c)


def gap_series(settings: StyleRemovalFigures) -> tuple[list[str], list[dict]]:
    """Daily return difference against no removal at equal volatility, mean of three schedules, anchored at zero.

    Each arm is scaled per schedule to the full-sample volatility of no removal, so the cumulative gap
    accumulates the Sharpe difference rather than a difference in risk taken.
    """
    frame = returns(settings.data).sort("date")
    first = (frame["date"][0] - dt.timedelta(days=1)).isoformat()
    dates = [first, *[d.isoformat() for d in frame["date"]]]
    data = []
    for arm, label, role, _, dash in settings.arms:
        diff = sum(frame[f"{arm}_o{k}"] * (frame[f"none_o{k}"].std() / frame[f"{arm}_o{k}"].std()) - frame[f"none_o{k}"]
                   for k in range(3)) / 3
        data.append(series(arm, label, role, [0.0, *diff.to_list()], additive=True, drawdown=False, dash=dash))
    return dates, data


def export_gap_chart(assets: Path, settings: StyleRemovalFigures) -> None:
    dates, data = gap_series(settings)
    write_chart(assets / "equal-vol-gap.json", dates, data, {"gap": dict(
        kind="performance", series=[s["id"] for s in data], additive=True,
        unit="Points vs no removal, equal volatility", statistics=False, zeroReference=True,
        showWindow=False, dateLabelSpacing=10,
        dateTicks=[dates[0], "2005-01-01", "2010-01-01", "2015-01-01", "2020-01-01", dates[-1]],
        mobileDateTicks=[dates[0], "2005-01-01", "2015-01-01", dates[-1]],
        start=dates[0], marker=f"{settings.split_year}-01-01", shade=[[f"{settings.split_year}-01-01", dates[-1]]],
        episodes=[["1999–2018", dates[0], "2018-12-31"], ["2019–2026", "2018-12-31", dates[-1]]],
        note="Sum of daily net return differences against no removal, each variant scaled to the volatility of no removal, mean of three rebalance schedules, points of capital. Shaded: 2019 onward.")})


def render_gap(out: Path, dark: bool, mobile: bool, settings: StyleRemovalFigures) -> None:
    c = palette(dark)
    dates, data = gap_series(settings)
    x = [dt.date.fromisoformat(d) for d in dates]
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "style-removal-gap"}):
        fig, ax = plt.subplots(figsize=(4.4, 4.0) if mobile else (9.4, 3.9))
        fig.set_facecolor(c["bg"]); style(ax, c, mobile)
        ax.axhline(0, color=c["ink"], lw=0.8)
        ax.axvspan(dt.date(settings.split_year, 1, 1), x[-1], color=c["grid"], alpha=0.55, zorder=0)
        cumulative = {}
        for (arm, label, _, colour, dash), s in zip(settings.arms, data):
            values = [0.0]
            for v in s["values"][1:]:
                values.append(values[-1] + v * 100)
            cumulative[arm] = values
            ax.plot(x, values, color=c[colour], lw=1.7, ls="--" if dash == "dash" else "-")
            ax.text(x[-1] + dt.timedelta(days=150), values[-1], label, va="center", fontsize=10, color=c[colour])
        ax.set_xlim(x[0], x[-1] + dt.timedelta(days=(900 if mobile else 1000)))
        ticks = (2005, 2015) if mobile else (2005, 2010, 2015, 2020)
        ax.set_xticks([x[0], *[dt.date(y, 1, 1) for y in ticks]], [str(x[0].year), *map(str, ticks)])
        save(fig, out / f"equal-vol-gap{suffix(dark, mobile)}.svg", c)


def export(assets: Path, *, settings: StyleRemovalFigures = StyleRemovalFigures()) -> None:
    assets.mkdir(parents=True, exist_ok=True)
    export_gap_chart(assets, settings)
    for dark in (False, True):
        for mobile in (False, True):
            render_diagram(assets, dark, mobile)
            for render in (render_shares, render_risk_return, render_deltas):
                render(assets, dark, mobile, settings.data)
            render_gap(assets, dark, mobile, settings)


if __name__ == "__main__":
    export(Path(__file__).resolve().parents[1] / "assets/ridge-style-removal")
