"""Interactive displays of the retained portfolio-construction figure inputs."""
from __future__ import annotations
import argparse
import json
from datetime import timedelta
from pathlib import Path
import polars as pl
from blog_charts import series, write_chart


def export(inputs: Path, assets: Path, market: Path) -> None:
    source = json.loads(market.read_text())
    index = next(s for s in source["series"] if s["role"] == "index")
    benchmark = dict(zip(source["dates"], index["values"], strict=True))
    models = [("volatility_scaled", "Volatility-scaled", "comparison"),
              ("optimizer_with_trading_controls", "Optimizer + trading controls", "strategy")]
    daily = pl.scan_parquet(inputs / "performance_path_daily.parquet").filter(pl.col("date") <= pl.date(2021,12,31)).sort("date").collect()
    paths, dates = [], None
    for key, label, role in models:
        part = daily.filter(pl.col("allocator") == key)
        current = [(part["date"][0] - timedelta(days=1)).isoformat(), *[d.isoformat() for d in part["date"]]]
        if dates is not None and dates != current: raise ValueError("Calendars differ")
        dates = current
        wealth = [1.0, *part["wealth"].to_list()]
        paths.append(series(key, label, role, [0.0, *[b/a-1 for a,b in zip(wealth,wealth[1:])]]))
    paths.append(series("index", "Russell 1000", "index", [0.0,*[benchmark[d]/source["scale"] for d in dates[1:]]]))
    write_chart(assets / "performance.json", dates, paths, {"performance": dict(kind="performance", series=[p["id"] for p in paths],log=True,drawdown=True,
        episodes=[["2008–09","2007-12-31","2009-12-31"],["2020–21","2019-12-31","2021-12-31"]],
        note="Statistics of the plotted mean wealth path. Each schedule compounds separately; Table 2 reports means of per-schedule statistics. Zero-cash Sharpe.")})
    beta = (pl.scan_csv(inputs / "rolling_realised_beta_252d.csv",try_parse_dates=True)
            .filter(pl.col("date") <= pl.date(2021,12,31))
            .group_by("allocator","date").agg(pl.col("realised_beta_252d").mean()).sort("date").collect())
    lines, dates = [], None
    for key,label,role in models:
        part = beta.filter(pl.col("allocator") == key)
        # Keep the source figure's month-end observations and its warm-up.
        part = part.group_by(pl.col("date").dt.strftime("%Y-%m").alias("month"),maintain_order=True).last()
        current = [d.isoformat() for d in part["date"]]
        if dates is not None and dates != current: raise ValueError("Beta calendars differ")
        dates = current
        lines.append(series(key,label,role,part["realised_beta_252d"].to_list()))
    write_chart(assets / "beta.json",dates,lines,{"beta":dict(kind="values",series=[s["id"] for s in lines],unit="Trailing 252-session market beta",band=[-.05,.05])})
    ladder = pl.scan_csv(inputs / "rho_ladder_summary.csv").sort("rho").collect()
    panels=[]
    metrics = [
        ("realised_to_predicted_volatility", "Risk calibration", [0.5, 1.6], [0.5, 1, 1.5], 1),
        ("beta_mean_error", "Beta bias", [0, .08], [0, .04, .08], 0),
        ("executed_turnover_l1_annualized", "Turnover (× capital/yr)", [0, 30], [0, 15, 30], None),
        ("net_sharpe", "Net Sharpe", [0, 1.5], [0, .75, 1.5], None),
    ]
    for key, title, domain, ticks, reference in metrics:
        panels.append(dict(x=ladder["rho"].to_list(), y=ladder[key].to_list(), title=title,
                           xTitle="Correlation shrinkage", selected=.5, domain=domain,
                           yTicks=ticks, ticks=[0, .5, 1], reference=reference))
    chart = dict(kind="panels", sharedX="Correlation shrinkage", panels=panels)
    charts = {"shrinkage": chart}
    (assets / "comparisons.json").write_text(json.dumps(dict(version=1, charts=charts), separators=(",", ":"))+"\n")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs",type=Path,required=True)
    parser.add_argument("--assets",type=Path,default=Path("assets/joint-sizing"))
    parser.add_argument("--market",type=Path,default=Path("assets/low-volatility-sizing/performance.json"))
    args=parser.parse_args();export(args.inputs,args.assets,args.market)
