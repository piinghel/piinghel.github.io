"""Interactive displays for the momentum-crash article.

Development-only WML context comes from the public study. The full-history
relative P&L uses the verified Ridge continuation, retaining every first trade.
Only portfolio aggregates are exported.
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
import polars as pl
from blog_charts import series, write_chart

@dataclass(frozen=True)
class MomentumEvidence:
    evidence: Path = Path("/Users/pjinghelbrecht/ResearchLocal/quant_research/projects/momentum_crashes_public/outputs/evidence")
    holdout: Path = Path("/Users/pjinghelbrecht/ResearchLocal/quant_research/data/runs/momentum_crash_holdout_20261001")
    start: dt.date = dt.date(1998, 9, 1)
    end: dt.date = dt.date(2021, 12, 31)
    display_rules: tuple[tuple[str, str, str, str], ...] = (
        ("overlay", "score_overlay", "Score overlay", "long"),
        ("learned", "learned_interactions", "Learned interactions", "size"),
        ("cap", "optimizer_cap", "Optimizer cap", "cash"),
    )


def export(assets: Path, *, settings: MomentumEvidence = MomentumEvidence()) -> None:
    wml = pl.read_parquet(settings.evidence / "momentum_deciles.parquet").filter(pl.col("date").is_between(settings.start, settings.end)).sort("date")
    crash = [series(k, label, role, [0.0, *wml[k].cast(pl.Float64).fill_null(0.0).to_list()[1:]])
             for k, label, role in (("winners", "Winners", "long"), ("losers", "Losers", "short"), ("wml", "Long–short (WML)", "strategy"))]
    write_chart(assets / "crash-2009.json", [d.isoformat() for d in wml["date"]], crash, {"crash": dict(
        kind="performance", series=[s["id"] for s in crash],
        episodes=[["2000–02", "2000-06-30", "2002-12-31"], ["2008–09", "2007-07-02", "2010-06-30"],
                  ["2016", "2015-06-30", "2016-12-30"], ["2020–21", "2019-12-31", "2021-06-30"]],
        directLabels=True, showLegend=False, shade=[["2009-03-09", "2009-05-29"], ["2020-11-09", "2020-11-13"]],
        note="Equal-weight 12-1 momentum deciles within the Russell 1000, formed at month ends.")})

    # Differencing the verified cumulative path preserves the original three-schedule
    # denominator, including zero cash before each schedule's first genuine trade.
    saved = pl.scan_csv(settings.holdout / "chart_added_pnl.csv", try_parse_dates=True).filter(
        pl.col("variant").is_in([rule for _, rule, _, _ in settings.display_rules])).collect()
    added, dates = [], None
    for key, rule, label, role in settings.display_rules:
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
        unit="Added P&L vs baseline (points)", statistics=False, zeroReference=True,
        showWindow=False, dateLabelSpacing=10,
        dateTicks=[dates[0], "2005-01-01", "2010-01-01", "2015-01-01", "2020-01-01", dates[-1]],
        mobileDateTicks=[dates[0], "2005-01-01", "2015-01-01", dates[-1]],
        periodLabels=[dict(date="2000-01-01", text="Training", mobileText="Training", y=.03),
                      dict(date="2024-03-01", text="Test: 2022–2026", mobileText="Test", y=.03)],
        start=dates[0], marker="2022-01-01", shade=[["2022-01-01", dates[-1]]],
        episodes=[["Development", dates[0], "2021-12-31"], ["Test: 2022–2026", "2021-12-31", dates[-1]]],
        note="Sum of daily net return differences against Ridge, mean of three schedules, points of capital. No strategy P&L before September 1998. Shaded: 2022–May 2026. Table 3 reports portfolio Sharpe and drawdown.")})


if __name__ == "__main__":
    export(Path("assets/momentum-crashes-ridge"))
