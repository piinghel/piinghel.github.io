"""Interactive displays for the momentum-crash article (development period only).

Reads the portfolio-level evidence of the public study (piinghel/momentum-crash-study).
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import polars as pl
from blog_charts import series, write_chart

EVIDENCE = Path("/Users/pjinghelbrecht/Documents/quant_research/projects/momentum_crashes_public/outputs/evidence")
START, END = dt.date(1998, 9, 1), dt.date(2021, 12, 31)
EPISODES = [["2008–09", "2007-12-31", "2009-12-31"], ["2020–21", "2019-12-31", "2021-12-31"]]


def schedules(returns: pl.DataFrame, rule: str) -> pl.DataFrame:
    """Daily net returns of one rule, one column per rebalance schedule."""
    return (returns.filter(pl.col("rule") == rule)
            .pivot(on="schedule", index="date", values="net_return").drop_nulls().sort("date").select("date", "o0", "o1", "o2"))


def mean_wealth_returns(frame: pl.DataFrame) -> tuple[list[str], list[float]]:
    """Daily returns of the mean of the three separately compounded schedule wealth paths."""
    wealth = [1.0, *frame.select(sum((1 + pl.col(o)).cum_prod() for o in ("o0", "o1", "o2")) / 3).to_series().to_list()]
    first = (frame["date"][0] - dt.timedelta(days=1)).isoformat()
    return [first, *[d.isoformat() for d in frame["date"]]], [0.0, *[b / a - 1 for a, b in zip(wealth, wealth[1:])]]


def export(assets: Path) -> None:
    returns = pl.read_parquet(EVIDENCE / "schedule_returns.parquet").filter(pl.col("date").is_between(START, END))
    rules = {rule: schedules(returns, rule) for rule in returns["rule"].unique()}
    paths, dates = [], None
    for key, rule, label, role, opts in (
            ("baseline", "baseline", "Baseline", "comparison", {}),
            ("overlay", "score_overlay", "Score overlay", "long", {}),
            ("constant", "constant_shrink", "Constant shrink", "short", {"visible": False, "dash": "dot"}),
            ("learned", "learned_interactions", "Learned interactions", "size", {"visible": False}),
            ("cap", "optimizer_cap", "Optimizer cap", "cash", {"visible": False}),
            ("combined", "learned_plus_overlay", "Learned + overlay", "hedged", {"visible": False})):
        current, values = mean_wealth_returns(rules[rule])
        if dates is not None and dates != current:
            raise ValueError("Calendars differ")
        dates = current
        paths.append(series(key, label, role, values, **opts))
    write_chart(assets / "performance.json", dates, paths, {"performance": dict(kind="performance", series=[p["id"] for p in paths],
        log=True, drawdown=True, episodes=EPISODES,
        note="Statistics of the plotted mean wealth path. Each schedule compounds separately; Table 2 reports means of per-schedule statistics. Zero-cash Sharpe.")})

    wml = pl.read_parquet(EVIDENCE / "momentum_deciles.parquet").filter(pl.col("date").is_between(START, END)).sort("date")
    crash = [series(k, label, role, [0.0, *wml[k].cast(pl.Float64).fill_null(0.0).to_list()[1:]])
             for k, label, role in (("winners", "Winners", "long"), ("losers", "Losers", "short"), ("wml", "Long–short (WML)", "strategy"))]
    write_chart(assets / "crash-2009.json", [d.isoformat() for d in wml["date"]], crash, {"crash": dict(
        kind="performance", series=[s["id"] for s in crash], initialRange=["2007-07-02", "2010-06-30"],
        episodes=[["2000–02", "2000-06-30", "2002-12-31"], ["2008–09", "2007-07-02", "2010-06-30"],
                  ["2016", "2015-06-30", "2016-12-30"], ["2020–21", "2019-12-31", "2021-06-30"]],
        directLabels=True, exploreOpen=True, shade=[["2009-03-09", "2009-05-29"], ["2020-11-09", "2020-11-13"]],
        note="Equal-weight 12-1 momentum deciles within the Russell 1000, formed at month ends.")})

    mean = {rule: frame.select("date", ((pl.col("o0") + pl.col("o1") + pl.col("o2")) / 3).alias("r")) for rule, frame in rules.items()}
    added = []
    for key, rule, label, role, opts in (
            ("overlay", "score_overlay", "Score overlay", "long", {}),
            ("learned", "learned_interactions", "Learned interactions", "size", {}),
            ("combined", "learned_plus_overlay", "Learned + overlay", "hedged", {}),
            ("cap", "optimizer_cap", "Optimizer cap", "cash", {}),
            ("constant", "constant_shrink", "Constant shrink", "comparison", {"dash": "dot"})):
        diff = mean[rule].join(mean["baseline"], on="date", suffix="_b")
        values = (diff["r"] - diff["r_b"]).to_list()
        dates = [d.isoformat() for d in diff["date"]]
        added.append(series(key, label, role, [0.0, *values[1:]], additive=True, drawdown=False, **opts))
    write_chart(assets / "value-added.json", dates, added, {"added": dict(kind="performance", series=[s["id"] for s in added], additive=True,
        episodes=EPISODES, shade=[["2009-01-01", "2009-12-31"], ["2020-01-01", "2020-12-31"]],
        note="Sum of daily net return differences against the baseline, mean of the three schedules, points of capital.")})


if __name__ == "__main__":
    export(Path("assets/momentum-crashes"))
