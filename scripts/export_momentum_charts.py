"""Interactive displays for the momentum-crash article (development period only)."""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import polars as pl
from blog_charts import series, write_chart

QR = Path("/Users/pjinghelbrecht/Documents/quant_research/data")
STUDY, REVIEW = QR / "momentum_crash_layers_20260929", QR / "momentum_crash_layers_review_20260930"
START, END = dt.date(1998, 9, 1), dt.date(2021, 12, 31)


def schedule_mean(folder: Path) -> pl.DataFrame:
    arm = next(p for p in (folder / "replay").glob("*") if (p / "manifest.json").exists())
    parts = [pl.read_csv(arm / "calendars" / o / "returns.csv", try_parse_dates=True)
             .with_columns(pl.col("date").cast(pl.Date)).filter(pl.col("date").is_between(START, END))
             .select("date", pl.col("long_short_net").alias(o)) for o in ("o0", "o1", "o2")]
    frame = parts[0].join(parts[1], on="date").join(parts[2], on="date").sort("date")
    return frame.select("date", ((pl.col("o0") + pl.col("o1") + pl.col("o2")) / 3).alias("r"))


def export(assets: Path) -> None:
    wml = (pl.read_parquet(STUDY / "states/wml_returns.parquet")
           .filter(pl.col("date").is_between(dt.date(2009, 3, 6), dt.date(2009, 8, 31))).sort("date"))
    dates = [d.isoformat() for d in wml["date"]]
    crash = [series(k, label, role, [0.0, *wml[k].cast(pl.Float64).to_list()[1:]])
             for k, label, role in (("winners", "Winners", "long"), ("losers", "Losers", "short"), ("wml", "Long–short (WML)", "strategy"))]
    write_chart(assets / "crash-2009.json", dates, crash, {"crash": dict(kind="performance", series=[s["id"] for s in crash],
        shade=[["2009-03-09", "2009-05-29"]], note="Equal-weight 12-1 momentum deciles within the Russell 1000, formed at month ends.")})
    base = schedule_mean(STUDY / "runs_ridge/saved")
    rules = (("overlay", "Score overlay", "strategy", STUDY / "runs_ridge/s_bsc_var_l100", {}),
             ("constant", "Constant shrink", "comparison", REVIEW / "runs/ridge/const_348", {"dash": "dot"}))
    added = []
    for key, label, role, folder, opts in rules:
        diff = schedule_mean(folder).join(base, on="date", suffix="_b")
        values = (diff["r"] - diff["r_b"]).to_list()
        dates = [d.isoformat() for d in diff["date"]]
        added.append(series(key, label, role, [0.0, *values[1:]], additive=True, drawdown=False, **opts))
    write_chart(assets / "value-added.json", dates, added, {"added": dict(kind="performance", series=[s["id"] for s in added], additive=True,
        shade=[["2009-01-01", "2009-12-31"], ["2020-01-01", "2020-12-31"]],
        note="Sum of daily net return differences against the baseline, mean of the three schedules, points of capital.")})


if __name__ == "__main__":
    export(Path("assets/momentum-crashes"))
