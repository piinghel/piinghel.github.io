"""Export finalized portfolio aggregates for the low-volatility article.

Usage: python scripts/export_low_vol_charts.py --baseline /path/to/saved/run
       --hedge /path/to/saved/hedge
"""
from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

import polars as pl

from blog_charts import series, statistics, write_chart


def read_series(path, scenario, expression):
    return (pl.scan_parquet(path).filter(pl.col("scenario") == scenario)
            .select("date", expression.alias("return")).sort("date").collect())


def equal_universe(baseline):
    """Combine before-cost decile P&L at exact per-stock equal weights."""
    universe = pl.scan_csv(baseline / "eligible_universe.csv", try_parse_dates=True).rename({"date": "signal_date"})
    raw = pl.scan_parquet(baseline / "decile_daily.parquet")
    panel = (raw.select("date", "signal_date", "scenario", "gross_return")
             .with_columns(pl.col("scenario").str.extract(r"(\d+)$", 1).cast(pl.Int64).alias("decile"))
             .join(universe, on="signal_date", how="left", validate="m:1")
             .with_columns((((pl.col("decile") * pl.col("eligible_stocks") + 9) // 10)
                            - (((pl.col("decile") - 1) * pl.col("eligible_stocks") + 9) // 10)).alias("count"))
             .sort("date", "decile").collect())
    if panel.null_count().row(0) != (0,) * panel.width:
        raise ValueError("Incomplete decile/universe join")
    if not panel["gross_return"].is_finite().all():
        raise ValueError("Invalid decile P&L")
    checks = (panel.lazy().group_by("date").agg(pl.len().alias("rows"),
              pl.col("decile").n_unique().alias("deciles"),
              pl.col("signal_date").n_unique().alias("signals"),
              (pl.col("count").sum() == pl.col("eligible_stocks").first()).alias("counts_match")).collect())
    if not all(r["rows"] == r["deciles"] == 10 and r["signals"] == 1 and r["counts_match"] for r in checks.to_dicts()):
        raise ValueError("Incomplete decile partition")
    schedule = pl.scan_csv(baseline / "execution_schedule.csv", try_parse_dates=True).select("signal_date", "effective_return_date").sort("effective_return_date")
    mapping = (panel.lazy().select("date", "signal_date").unique().sort("date")
               .join_asof(schedule.rename({"signal_date": "expected_signal"}),
                          left_on="date", right_on="effective_return_date", strategy="backward").collect())
    if mapping["signal_date"].to_list() != mapping["expected_signal"].to_list():
        raise ValueError("Daily signal timing differs from retained schedule")
    extremes = (panel.lazy().filter(pl.col("decile").is_in([1, 10]))
                .select("signal_date", "decile", "count").unique()
                .with_columns(pl.when(pl.col("decile") == 1).then(pl.lit("low_vol_long"))
                              .otherwise(pl.lit("high_vol_long")).alias("scenario"))
                .join(pl.scan_csv(baseline / "target_exposures.csv", try_parse_dates=True),
                      on=["signal_date", "scenario"], how="left", validate="1:1")
                .select("count", "positions").collect())
    if extremes["count"].to_list() != extremes["positions"].to_list():
        raise ValueError("Inferred counts differ from saved target holdings")
    return (panel.lazy().group_by("date")
            .agg((pl.col("gross_return") * pl.col("count") / pl.col("eligible_stocks")).sum().alias("return"))
            .sort("date").collect())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--hedge", required=True, type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path("assets/2024-12-15-low-volatility-factor"))
    args = parser.parse_args()
    base = args.baseline / "stage_daily.parquet"
    frames = [
        ("strategy", "Inverse-volatility", "strategy", read_series(base, "vol_scaled_ls", pl.col("net_return")), {}),
        ("equal", "Equal-weight", "comparison", read_series(base, "naive_equal_ls", pl.col("net_return")), {"visible": False}),
        ("hedged", "Equal-weight + beta hedge", "hedged", read_series(args.hedge / "daily.parquet", "naive_equal_ls", pl.col("net_return") + pl.col("hedge_gross_return") - pl.col("hedge_cost")), {"dash": "dash"}),
        ("hedged_strategy", "Inverse-volatility + beta hedge", "strategy", read_series(args.hedge / "daily.parquet", "vol_scaled_ls", pl.col("net_return") + pl.col("hedge_gross_return") - pl.col("hedge_cost")), {"dash": "dot", "visible": False}),
        ("index", "Russell 1000", "index", read_series(base, "vol_scaled_ls", pl.col("market_return")), {}),
        ("gross", "Inverse-volatility", "strategy", read_series(base, "vol_scaled_ls", pl.col("gross_return")), {}),
        ("long", "Long book", "long", read_series(args.baseline / "scaled_leg_daily.parquet", "scaled_long_leg", pl.col("portfolio_relative_value") - 1), {"contribution": True, "parent": "gross"}),
        ("short", "Short book", "short", read_series(args.baseline / "scaled_leg_daily.parquet", "scaled_short_leg", pl.col("portfolio_relative_value") - 1), {"contribution": True, "parent": "gross"}),
    ]
    dates = frames[0][3]["date"].to_list()
    for _, _, _, frame, _ in frames:
        if frame["date"].to_list() != dates or frame["return"].null_count():
            raise ValueError("Incomplete or misaligned series")
    episodes = [
        ["Dot-com rally", "1998-10-08", "2000-03-09"],
        ["2008–09", "2008-01-01", "2009-12-31"],
        ["2020 rebound", "2020-03-23", "2020-12-31"],
        ["Post-2021", "2022-01-01", "2026-05-27"],
        ["2025–26 rally", "2025-04-03", "2026-05-27"],
    ]
    charts = {
        "performance": dict(kind="performance", series=["strategy", "equal", "hedged", "index"],
                            drawdown=True, log=True, benchmark=False, episodes=episodes,
                            note="After costs · growth from 100 at the selected start. Annual return compounds; Sharpe assumes zero cash return. 252 sessions/year."),
        "rally-a": dict(kind="performance", series=["gross", "index", "long", "short"],
                        heading="A · Dot-com rally, then reversal", statisticsOpen=False,
                        growthRange=[60, 170], contributionRange=[-30, 20],
                        start="1998-10-08", end="2001-04-03", benchmark=True, contributions=True,
                        episodes=[episodes[0]], marker="2000-03-09",
                        note="A · Dot-com rally, then reversal. Before costs; 100 at the first visible close. Book contributions link daily P&L to the preceding strategy value, in percentage points."),
        "rally-b": dict(kind="performance", series=["gross", "index", "long", "short"],
                        heading="B · April 2025–May 2026 rally", statisticsOpen=False,
                        growthRange=[60, 170], contributionRange=[-30, 20],
                        start="2025-04-03", end="2026-05-27", benchmark=True, contributions=True,
                        note="B · April 2025–May 2026 rally. Before costs; 100 at the first visible close. Book contributions are not standalone investment returns."),
    }
    # Retain the original first return in the full window via an explicit capital anchor.
    anchor = (dates[0] - timedelta(days=1)).isoformat()
    write_chart(args.output / "performance.json", [anchor] + [d.isoformat() for d in dates],
                [series(key, label, role, [0.0] + frame["return"].to_list(), **options)
                 for key, label, role, frame, options in frames if key in charts["performance"]["series"]],
                {"performance": charts["performance"]})
    episode_indices = [i for i, d in enumerate(dates)
                       if "1998-10-08" <= d.isoformat() <= "2001-04-03"
                       or "2025-04-03" <= d.isoformat() <= "2026-05-27"]
    write_chart(args.output / "episodes.json", [dates[i].isoformat() for i in episode_indices],
                [series(key, label, role, [frame["return"][i] for i in episode_indices], **options)
                 for key, label, role, frame, options in frames if key in charts["rally-a"]["series"]],
                {key: charts[key] for key in ["rally-a", "rally-b"]})
    deciles = []
    saved_deciles = pl.scan_csv(args.baseline / "decile_metrics.csv").collect()
    for i in range(1, 11):
        frame = read_series(args.baseline / "decile_daily.parquet", f"decile_{i}", pl.col("gross_return"))
        if frame["date"].to_list() != dates:
            raise ValueError("Decile calendar mismatch")
        values = frame["return"].to_list()
        computed = statistics(values)
        expected = next(r for r in saved_deciles.to_dicts() if r["scenario"] == f"decile_{i}")
        for key, column in [("annual_return", "geometric_return"), ("volatility", "volatility"), ("sharpe", "sharpe_ratio")]:
            assert abs(computed[key] - expected[column]) < 1e-11, (i, key)
        deciles.append(series(f"decile_{i}", str(i), "long" if i == 1 else "short" if i == 10 else "comparison", values))
    equal = equal_universe(args.baseline)
    if equal["date"].to_list() != dates:
        raise ValueError("Equal-weight universe calendar mismatch")
    deciles.append(series("equal_universe", "Equal-weight universe", "hedged", equal["return"].to_list(), visible=False, tick="EW"))
    deciles.append(series("index", "Russell 1000", "index", frames[4][3]["return"].to_list(), tick="R1000"))
    write_chart(args.output / "deciles.json", [d.isoformat() for d in dates], deciles,
                {"deciles": dict(kind="bars", series=[s["id"] for s in deciles], episodes=episodes,
                                 note="Before costs · daily returns on the selected dates, inclusive. Annual return compounds; volatility and zero-cash Sharpe use 252 sessions/year. Decile 1: lowest volatility; decile 10: highest. EW: all eligible stocks, equal weights at each three-week rebalance. R1000: Russell 1000.")})
    print("Equal-weight universe", statistics(equal["return"].to_list()))
    for key, label, _, frame, _ in frames[:4]:
        print(label, statistics(frame["return"].to_list()))


if __name__ == "__main__":
    main()
