"""Interactive displays for the momentum-crash article.

Development-only WML context comes from the public study. The full-history
relative P&L uses the verified Ridge continuation, retaining every first trade.
Only portfolio aggregates are exported.
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import polars as pl
from blog_charts import series, write_chart

EVIDENCE = Path("/Users/pjinghelbrecht/Documents/quant_research/projects/momentum_crashes_public/outputs/evidence")
HOLDOUT = Path("/Users/pjinghelbrecht/Documents/quant_research/data/momentum_crash_holdout_20261001")
START, END = dt.date(1998, 9, 1), dt.date(2021, 12, 31)
DISPLAY_RULES = (
    ("overlay", "score_overlay", "Score overlay", "long"),
    ("learned", "learned_interactions", "Learned interactions", "size"),
    ("cap", "optimizer_cap", "Optimizer cap", "cash"),
)


def export(assets: Path) -> None:
    wml = pl.read_parquet(EVIDENCE / "momentum_deciles.parquet").filter(pl.col("date").is_between(START, END)).sort("date")
    crash = [series(k, label, role, [0.0, *wml[k].cast(pl.Float64).fill_null(0.0).to_list()[1:]])
             for k, label, role in (("winners", "Winners", "long"), ("losers", "Losers", "short"), ("wml", "Long–short (WML)", "strategy"))]
    write_chart(assets / "crash-2009.json", [d.isoformat() for d in wml["date"]], crash, {"crash": dict(
        kind="performance", series=[s["id"] for s in crash], initialRange=["2007-07-02", "2010-06-30"],
        episodes=[["2000–02", "2000-06-30", "2002-12-31"], ["2008–09", "2007-07-02", "2010-06-30"],
                  ["2016", "2015-06-30", "2016-12-30"], ["2020–21", "2019-12-31", "2021-06-30"]],
        directLabels=True, exploreOpen=True, shade=[["2009-03-09", "2009-05-29"], ["2020-11-09", "2020-11-13"]],
        note="Equal-weight 12-1 momentum deciles within the Russell 1000, formed at month ends.")})

    # Differencing the verified cumulative path preserves the original three-schedule
    # denominator, including zero cash before each schedule's first genuine trade.
    saved = pl.scan_csv(HOLDOUT / "chart_added_pnl.csv", try_parse_dates=True).filter(
        pl.col("variant").is_in([rule for _, rule, _, _ in DISPLAY_RULES])).collect()
    added, dates = [], None
    for key, rule, label, role in DISPLAY_RULES:
        frame = saved.filter(pl.col("variant") == rule).sort("date")
        first = (frame["date"][0] - dt.timedelta(days=1)).isoformat()
        current = [first, *[d.isoformat() for d in frame["date"]]]
        if dates is not None and dates != current:
            raise ValueError("Calendars differ")
        dates = current
        points = [0.0, *frame["points"].to_list()]
        values = [0.0, *[(b - a) / 100 for a, b in zip(points, points[1:])]]
        added.append(series(key, label, role, values, additive=True, drawdown=False))
    write_chart(assets / "value-added.json", dates, added, {"added": dict(
        kind="performance", series=[s["id"] for s in added], additive=True,
        start="1995-01-01", marker="2022-01-01", shade=[["2022-01-01", dates[-1]]],
        episodes=[["Development", dates[0], "2021-12-31"], ["Test: 2022–2026", "2021-12-31", dates[-1]]],
        note="Sum of daily net return differences against Ridge, mean of three schedules, points of capital. No strategy P&L before September 1998. Shaded: 2022–May 2026. Statistics here describe relative returns; Table 3 reports portfolio Sharpe and drawdown.")})


if __name__ == "__main__":
    export(Path("assets/momentum-crashes"))
