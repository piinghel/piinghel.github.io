"""Static figures for the momentum-crash article, with full-history relative P&L.

Sharpe and maximum drawdown by rule use the verified schedule means and lowest/highest
schedule Sharpe ratios (projects/momentum_crashes/evidence/review/ridge_stats.csv,
review_ridge_stats.csv). Sharpe by momentum-risk bucket is computed from the portfolio-level
evidence exported for the public study (projects/momentum_crashes_public/outputs/evidence).
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import polars as pl
from types import MappingProxyType

from export_momentum_charts import MomentumEvidence
from figure_svg import save_svg, svg_path

# Lagged momentum-risk state g (WML volatility over its expanding median, floored at 1); thresholds fixed before plotting.
# The five-session smoothing lets g decay towards 1, so "calm" allows 1e-4 (a removed share below 0.0002).
BUCKETS = (("Calm", "≤1×", 1.0, 1.0001), ("Elevated", "1–1.5×", 1.0001, 1.5),
           ("High", "1.5–2×", 1.5, 2.0), ("Extreme", "≥2×", 2.0, float("inf")))

# label, Sharpe mean/low/high, compounded max drawdown % mean/low/high (per schedule), family
ROWS = (
    ("Baseline", 1.317, 1.256, 1.358, 15.5, 14.9, 16.0, "base"),
    ("Score overlay", 1.541, 1.441, 1.612, 11.9, 10.8, 12.6, "overlay"),
    ("Learned interactions", 1.547, 1.481, 1.613, 13.3, 12.0, 14.7, "learned"),
    ("Optimizer cap", 1.469, 1.411, 1.525, 11.4, 10.6, 12.2, "cap"),
)
MARKER = MappingProxyType({"base": "o", "cap": "s", "overlay": "^", "learned": "D"})


def palette(dark: bool) -> dict[str, str]:
    return {"bg": "#0d1117" if dark else "#ffffff", "ink": "#e4e7ea" if dark else "#25313a",
            "muted": "#9ba5af" if dark else "#59636e", "grid": "#37414a" if dark else "#e2e6e9",
            "base": "#a0acb4" if dark else "#606e77",
            "cap": "#85b9aa" if dark else "#427a70", "overlay": "#89b5cc" if dark else "#426e89",
            "learned": "#c4a36f" if dark else "#896835"}


def render(out: Path, dark: bool, mobile: bool, *, rows=ROWS, markers=MARKER) -> None:
    c = palette(dark)
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "momentum-sharpe"}):
        if mobile:
            fig, axes = plt.subplots(2, 1, figsize=(3.9, 5.5), gridspec_kw={"hspace": 0.5})
        else:
            fig, axes = plt.subplots(1, 2, figsize=(9.4, 2.7), sharey=True, gridspec_kw={"wspace": 0.12, "width_ratios": [1.2, 1]})
        fig.set_facecolor(c["bg"])
        ys = list(range(len(rows)))[::-1]
        # Drawdowns are plotted as negative numbers so that right means better in both panels.
        panels = [("Net Sharpe ratio", lambda r: (r[1], r[2], r[3]), (1.2, 1.65), [1.2, 1.4, 1.6] if mobile else [1.2, 1.3, 1.4, 1.5, 1.6]),
                  ("Maximum drawdown (%)", lambda r: (-r[4], -r[6], -r[5]), (-17, -9), [-16, -14, -12, -10])]
        for k, (ax, (title, get, lim, ticks)) in enumerate(zip(axes, panels)):
            ax.set_facecolor(c["bg"])
            base = get(rows[0])[0]
            ax.axvline(base, color=c["muted"], lw=0.8, ls=(0, (2, 3)), zorder=1)
            for y, row in zip(ys, rows):
                fam = row[-1]; m, lo, hi = get(row)
                ax.plot([lo, hi], [y, y], color=c[fam], lw=2.0, solid_capstyle="butt", zorder=2)
                ax.plot(m, y, markers[fam], ms=7.5, mfc=c[fam], mec=c[fam], mew=1.4, zorder=3)
            ax.set_xlim(*lim); ax.set_xticks(ticks)
            if k == 1:
                ax.set_xticklabels([f"{abs(t)}" if t else "0" for t in ticks])
            ax.tick_params(axis="x", colors=c["muted"], labelsize=10 if mobile else 10.5, length=0)
            ax.tick_params(axis="y", length=0, labelsize=10 if mobile else 11, pad=6)
            ax.grid(axis="x", color=c["grid"], lw=0.8); ax.set_axisbelow(True)
            for side in ax.spines.values(): side.set_visible(False)
            ax.set_title(title, loc="left", fontsize=11 if mobile else 11.5, color=c["ink"], pad=10)
            if k == 0 or mobile:
                ax.set_yticks(ys, [r[0] for r in rows])
                for tick, row in zip(ax.get_yticklabels(), rows):
                    tick.set_color(c["ink"])
            else:
                ax.tick_params(axis="y", labelleft=False)
        path = svg_path(out / "sharpe-by-rule", mobile=mobile, dark=dark)
        save_svg(fig, path, facecolor=c["bg"], tight_padding=0.12)


def sharpe_by_state(rules: tuple[str, ...] = ("baseline", "score_overlay"), *, settings: MomentumEvidence = MomentumEvidence(), buckets=BUCKETS) -> pl.DataFrame:
    """Net Sharpe per schedule within each state bucket, then averaged over schedules; share of trading days."""
    returns = pl.scan_parquet(settings.evidence / "schedule_returns.parquet").filter(
        pl.col("date") <= settings.end, pl.col("rule").is_in(rules)).collect().sort("date")
    state = pl.scan_parquet(settings.evidence / "momentum_state.parquet").filter(pl.col("date") <= settings.end).collect().sort("date")
    frame = returns.join_asof(state.select("date", "g"), on="date", strategy="backward")
    label = pl.lit(None, dtype=pl.String)
    for name, _, lo, hi in buckets:
        label = pl.when((pl.col("g") >= lo) & (pl.col("g") < hi)).then(pl.lit(name)).otherwise(label)
    per_schedule = (frame.with_columns(label.alias("bucket")).group_by("rule", "schedule", "bucket")
                    .agg(days=pl.len(), sharpe=pl.col("net_return").mean() / pl.col("net_return").std() * 252 ** 0.5))
    return (per_schedule.with_columns(share=pl.col("days") / pl.col("days").sum().over("rule", "schedule"))
            .group_by("rule", "bucket").agg(pl.col("sharpe").mean(), pl.col("sharpe").min().alias("low"),
                                            pl.col("sharpe").max().alias("high"), pl.col("share").mean()))


def render_state(out: Path, dark: bool, mobile: bool, *, settings: MomentumEvidence = MomentumEvidence(), buckets=BUCKETS) -> None:
    c = palette(dark)
    stats = {(r["rule"], r["bucket"]): r for r in sharpe_by_state(settings=settings, buckets=buckets).iter_rows(named=True)}
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "momentum-state"}):
        fig, ax = plt.subplots(figsize=(3.9, 2.7) if mobile else (7.4, 2.65))
        fig.subplots_adjust(left=.35 if mobile else .22, right=.96, top=.81, bottom=.18)
        fig.set_facecolor(c["bg"])
        ax.set_facecolor(c["bg"])
        ax.set(xlim=(0, 2), ylim=(-.55, len(buckets) - .45))
        ax.set_xticks([0, .5, 1, 1.5, 2], ["0", "0.5", "1", "1.5", "2"])
        ax.set_yticks([])
        ax.set_axisbelow(True)
        ax.grid(axis="x", color=c["grid"], lw=.7)
        ax.tick_params(axis="x", colors=c["muted"], labelsize=9, length=0, pad=3)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xlabel("Net Sharpe ratio", color=c["ink"], fontsize=10, labelpad=4)
        for i, (name, threshold, *_) in enumerate(buckets):
            y = len(buckets) - 1 - i
            baseline = stats[("baseline", name)]
            overlay = stats[("score_overlay", name)]["sharpe"]
            ax.text(-.05, y + .15, name, transform=ax.get_yaxis_transform(),
                    ha="right", va="center", color=c["ink"], fontsize=10.5)
            ax.text(-.05, y - .2, f"{threshold} · {baseline['share']:.0%}", transform=ax.get_yaxis_transform(),
                    ha="right", va="center", color=c["muted"], fontsize=8.5)
            ax.plot([baseline["sharpe"], overlay], [y, y], color=c["muted"], lw=1)
            ax.plot(baseline["sharpe"], y, marker="o", markersize=8.5, markerfacecolor=c["bg"],
                    markeredgecolor=c["base"], markeredgewidth=1.3, linestyle="none",
                    label="Baseline" if i == 0 else None)
            ax.plot(overlay, y, marker="D", markersize=4.5, color=c["overlay"], linestyle="none",
                    label="Score overlay" if i == 0 else None)
            if name == "Extreme":
                for value, side, colour in ((baseline["sharpe"], -1, c["base"]), (overlay, 1, c["overlay"])):
                    ax.annotate(f"{value:.2f}", (value, y), xytext=(side * 7, 0), textcoords="offset points",
                                ha="right" if side < 0 else "left", va="center", fontsize=9, color=colour)
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.05), ncol=2, frameon=False,
                  handlelength=1, handletextpad=.4, columnspacing=1.2, borderaxespad=0,
                  fontsize=9.5, labelcolor=c["ink"])
        path = svg_path(out / "sharpe-by-state", mobile=mobile, dark=dark)
        save_svg(fig, path, facecolor=c["bg"], tight_padding=0.12)


def render_added(out: Path, dark: bool, mobile: bool, *, settings: MomentumEvidence = MomentumEvidence()) -> None:
    """Fallback for the same saved cumulative differences as the interactive chart."""
    c = palette(dark)
    data = pl.scan_csv(settings.holdout / "chart_added_pnl.csv", try_parse_dates=True).filter(
        pl.col("variant").is_in([rule for _, rule, _, _ in settings.display_rules])).collect()
    start = data["date"].min() - dt.timedelta(days=1)
    end = data["date"].max()
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "momentum-added"}):
        fig, ax = plt.subplots(figsize=(4.4, 4.5) if mobile else (10, 4.8))
        fig.set_facecolor(c["bg"]); ax.set_facecolor(c["bg"])
        ax.axhline(0, color=c["ink"], lw=0.8)
        ax.axvspan(dt.date(2022, 1, 1), end, color=c["grid"], alpha=0.55, zorder=0)
        ax.axvline(dt.date(2022, 1, 1), color=c["muted"], lw=0.8, ls=":")
        for key, rule, label, _ in settings.display_rules:
            frame = data.filter(pl.col("variant") == rule).sort("date")
            anchor = frame["date"][0] - dt.timedelta(days=1)
            ax.plot([anchor, *frame["date"].to_list()], [0.0, *frame["points"].to_list()],
                    label=label, color=c[key], lw=1.6)
        years = (2005, 2015) if mobile else (2005, 2010, 2015, 2020)
        ax.set_xticks([start, *[dt.date(year, 1, 1) for year in years], end],
                      [str(start.year), *[str(year) for year in years], str(end.year)])
        ax.set_xlim(start, end)
        ax.set_title("Added P&L vs baseline (points)", loc="left", color=c["ink"], fontsize=11, pad=38 if mobile else 30)
        ax.text(dt.date(2024, 3, 1), .03, "Test" if mobile else "Test: 2022–2026", transform=ax.get_xaxis_transform(),
                ha="center", va="bottom", fontsize=9, color=c["ink"])
        ax.text(dt.date(2000, 1, 1), .96, "Training", transform=ax.get_xaxis_transform(),
                ha="center", fontsize=8, color=c["muted"])
        ax.tick_params(length=0, colors=c["muted"], labelsize=10)
        ax.grid(axis="y", color=c["grid"], lw=.7); ax.set_axisbelow(True)
        for spine in ax.spines.values(): spine.set_visible(False)
        legend = ax.legend(loc="lower left", bbox_to_anchor=(-.02, 1.01), ncol=2 if mobile else 3,
                           frameon=False, fontsize=9, handlelength=1.6)
        for item in legend.get_texts(): item.set_color(c["ink"])
        path = svg_path(out / "value-added", mobile=mobile, dark=dark)
        save_svg(fig, path, facecolor=c["bg"], tight_padding=0.12)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "assets/momentum-crashes-ridge"
    out.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        for mobile in (False, True):
            render(out, dark, mobile)
            render_state(out, dark, mobile)
            render_added(out, dark, mobile)
