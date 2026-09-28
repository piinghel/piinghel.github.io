"""Export the finalized regression comparison, without rerunning any portfolios."""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import polars as pl

from blog_charts import series, statistics, write_chart


def export(article: Path, assets: Path, market: Path) -> None:
    growth = pl.scan_csv(article / "growth_drawdown.csv").sort("date").collect()
    models = [("ridge_0p1", "Ridge", "strategy"), ("equal_weight", "Equal-weight", "comparison")]
    dates = growth.filter(pl.col("model") == models[0][0])["date"].to_list()
    anchor = (date.fromisoformat(dates[0]) - timedelta(days=1)).isoformat()
    paths = []
    for key, label, role in models:
        part = growth.filter(pl.col("model") == key)
        if part["date"].to_list() != dates:
            raise ValueError("Model calendars differ")
        wealth = [1.0, *part["growth_index"].to_list()]
        paths.append(series(key, label, role, [0.0, *[b / a - 1 for a, b in zip(wealth, wealth[1:])]]))
    source = json.loads(market.read_text())
    index = next(s for s in source["series"] if s["role"] == "index")
    returns = dict(zip(source["dates"], index["values"], strict=True))
    missing = set(dates) - returns.keys()
    if missing:
        raise ValueError(f"Missing market dates: {sorted(missing)}")
    paths.append(series("index", "Russell 1000", "index", [0.0, *[returns[d] / source["scale"] for d in dates]]))
    episodes = [["1998–2021", anchor, "2021-12-31"], ["After 2021", "2021-12-31", dates[-1]],
                ["2008–09", "2007-12-31", "2009-12-31"], ["2020–21", "2019-12-31", "2021-12-31"]]
    write_chart(assets / "performance.json", [anchor, *dates], paths, {
        "performance": dict(kind="performance", series=[s["id"] for s in paths], log=True,
                            drawdown=True, relative="ridge_0p1", marker="2022-01-03", episodes=episodes,
                            note="Compounded mean daily net P&L across three schedules; zero-cash Sharpe. Table 4 reports per-schedule statistics.")})
    bars = []
    calendar = None
    expected = pl.scan_csv(article / "deciles/decile_metrics.csv").collect()
    for key, label, role in models:
        score = "ridge" if key.startswith("ridge") else key
        daily = pl.scan_parquet(article / f"deciles/{score}_decile_daily.parquet").sort("date").collect()
        for decile in range(1, 11):
            part = daily.filter(pl.col("decile") == decile)
            current = [d.isoformat() for d in part["date"]]
            if calendar is not None and current != calendar:
                raise ValueError("Decile calendars differ")
            calendar = current
            values = part["ret"].to_list()
            for period, begin, end in [("development", "1998-01-01", "2021-12-31"), ("later", "2022-01-01", dates[-1])]:
                result = statistics([v for d, v in zip(calendar, values) if begin <= d <= end])
                row = expected.filter((pl.col("score") == score) & (pl.col("decile") == decile) & (pl.col("period") == period)).row(0, named=True)
                for metric in ("annual_return", "volatility", "sharpe"):
                    if abs(result[metric] - row[metric]) > 1e-6:
                        raise ValueError(f"Decile metric mismatch: {score}, {decile}, {period}, {metric}")
            bars.append(series(f"{score}_{decile}", f"{label} · {decile}", role, values, group=label, category=str(decile)))
    write_chart(assets / "deciles.json", calendar, bars, {
        "deciles": dict(kind="grouped-bars", series=[s["id"] for s in bars],
                        episodes=episodes, initialRange=[calendar[0], "2021-12-31"],
                        note="Before costs. Daily decile returns averaged across three schedules; zero-cash Sharpe.")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", required=True, type=Path)
    parser.add_argument("--assets", type=Path, default=Path("assets/multiple-linear-regression"))
    parser.add_argument("--market", type=Path, default=Path("assets/2024-12-15-low-volatility-factor/performance.json"))
    args = parser.parse_args()
    export(args.article, args.assets, args.market)
