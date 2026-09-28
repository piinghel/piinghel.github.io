"""Export only finalized daily portfolio and theme aggregates for both attribution parts."""
from __future__ import annotations
import argparse
import json
from datetime import timedelta
from pathlib import Path
import polars as pl
from blog_charts import SCALE, series, write_chart

FIELDS = [
    ("short_interest", "Short interest", "C_short_interest", "short_interest"),
    ("reversal", "Short-term return", "C_short_term_return", "reversal"),
    ("momentum", "Long-term return", "C_long_term_return", "momentum"),
    ("size", "Size", "C_size", "size"),
    ("activity", "Trading activity", None, "liquidity"),
    ("low_risk", "Low-risk package", None, "low_risk"),
    ("sector", "Sector tilt", "C_sector_tilt", "sector"),
    ("specific", "Stock-specific", "specific", "residual"),
    ("unloaded", "Unloaded holdings", "unloaded", "comparison"),
    ("cost", "Trading costs", None, "comparison"),
    ("low_volatility", "Low volatility", "C_low_volatility", "low_volatility"),
    ("beta", "Beta", "C_beta", "beta"),
    ("market", "Net market exposure", "C_net", "market"),
    ("turnover", "Turnover", "C_turnover", "liquidity"),
    ("volume", "Volume surge", "C_volume_surge", "liquidity"),
    ("price_volume", "Price-volume correlation", "C_price_volume_correlation", "liquidity"),
]


def export(themes: Path, history: Path, assets: Path) -> None:
    overview = json.loads((assets / "themes.json").read_text())
    windows = overview["windows"]
    drawdown_windows = sorted(windows)
    factor_columns = [column for _, _, column, _ in FIELDS if column and column.startswith("C_")]
    dates, output = None, []
    for leg in ("total", "long", "short"):
        frame=pl.scan_parquet(themes / f"daily_{leg}.parquet").filter(pl.col("date")>=pl.date(1999,1,1)).sort("date").collect()
        current=[d.isoformat() for d in frame["date"]]
        if dates is not None and dates!=current: raise ValueError("Leg calendars differ")
        dates=current
        for key,label,column,role in FIELDS:
            if key=="activity": values=frame["C_turnover"]+frame["C_volume_surge"]+frame["C_price_volume_correlation"]
            elif key=="low_risk": values=frame["C_low_volatility"]+frame["C_beta"]+frame["C_net"]
            elif key=="cost": values=frame["cost_"+leg]
            elif key=="specific":
                values=frame["R_loaded"]-frame.select(pl.sum_horizontal(factor_columns)).to_series()
            else: values=frame[column]
            output.append(series(leg+"_"+key,label,role,values.to_list()))
        output.append(series(leg+"_book","Whole book, net" if leg=="total" else leg.capitalize()+" leg, net","strategy",(frame["R"]+frame["cost_"+leg]).to_list()))
        if leg=="total":
            output.append(series("gross","Whole book, gross","strategy",frame["R"].to_list()))
    # Fixed, already-reviewed episode boundaries; no reclassification within a chosen window.
    episodes=(pl.scan_csv(themes / "regime_episodes.csv").filter((pl.col("leg")=="total")&(pl.col("theme")=="Book net"))
              .select("regime","start","end").unique().collect())
    masks={}
    for key,name in [("declines","decline"),("rallies","strong rally")]:
        intervals=episodes.filter(pl.col("regime")==name).select("start","end").rows()
        masks[key]=[int(any(a<=d<=b for a,b in intervals)) for d in dates]
    masks["rallies"]=[int(r and not d) for r,d in zip(masks["rallies"],masks["declines"],strict=True)]
    common=dict(series=[key for key,_,_,_ in FIELDS[:10]],components={"low_risk":["low_volatility","beta","market"],"activity":["turnover","volume","price_volume"]},
                episodes=[["1999–2003",dates[0],"2003-12-31"],["2008–09","2008-01-01","2009-12-31"],["2020–21","2020-01-01","2021-12-31"],["After 2021","2022-01-01",dates[-1]]])
    charts={"themes":dict(common,kind="attribution"),"years":dict(common,kind="attribution-years"),
            "regimes":dict(common,kind="attribution-regimes",masks=masks,focus="low_risk"),
            "drawdowns":dict(common,kind="attribution-drawdowns",windows=drawdown_windows)}
    # Verify the exported total reproduces the existing full-period overview.
    retained=overview["full"]
    for item in output[:len(FIELDS)]:
        if item["label"] in retained:
            annual=sum(item["values"])/SCALE/len(dates)*252*100
            if abs(annual-retained[item["label"]][0])>.001:
                raise ValueError(f"Full-period attribution differs: {item['label']}")
    charts["themes"]["legSource"]="/assets/portfolio-attribution/interactive-legs.json"
    write_chart(assets / "interactive-themes.json",dates,[s for s in output if s["id"].startswith("total_") or s["id"]=="gross"],charts)
    write_chart(assets / "interactive-legs.json",dates,[s for s in output if s["id"].startswith(("long_","short_"))],{})
    daily=pl.scan_parquet(history / "daily.parquet").sort("date").collect()
    dates=[(daily["date"][0]-timedelta(days=1)).isoformat(),*[d.isoformat() for d in daily["date"]]]
    paths=[]
    for key,label,column,role in [("long","Longs","long_pnl","long"),("short","Shorts","short_pnl","short"),("net","Net","long_short_net","strategy")]:
        paths.append(series(key,label,role,[0,*daily[column].to_list()],additive=True,drawdown=key=="net"))
    paths.append(series("index","Russell 1000","index",[0,*daily["benchmark"].to_list()],drawdown=False))
    write_chart(assets / "performance.json",dates,paths,{"performance":dict(kind="performance",series=[s["id"] for s in paths],additive=True,drawdown=True,
        shade=windows,
        episodes=[["2008–09",*drawdown_windows[0]],["2020–21",*drawdown_windows[1]]],
        note="Book P&L and drawdowns use fixed-notional points; annual return is the daily arithmetic mean × 252. Longs and shorts before costs, net after. Market shows compounded index change in percent; zero-cash Sharpe.")})


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--themes",type=Path,required=True)
    parser.add_argument("--history",type=Path,required=True)
    parser.add_argument("--assets",type=Path,default=Path("assets/portfolio-attribution"))
    args=parser.parse_args();export(args.themes,args.history,args.assets)
