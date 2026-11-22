"""Export the stock-ranking article's aggregate charts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date, timedelta
from itertools import accumulate
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import polars as pl
from blog_charts import series, write_chart


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def export(
    report: Path,
    profiles_path: Path,
    correlations_path: Path,
    *,
    models: tuple[tuple[str, str, str], ...] = (
        ("ridge", "Ridge", "equity_ridge"),
        ("lightgbm", "LightGBM", "equity_lightgbm"),
        ("kumo_small_4w", "Small 4w", "equity_small_four"),
        ("kumo_small", "Small 6w", "equity_small_six"),
        ("kumo_medium", "Medium", "equity_medium"),
        ("kumo_small_roll3", "Small rolling", "equity_rolling"),
    ),
    periods: tuple[str, ...] = ("1999–2021", "1999–2011", "2012–2021", "2017–2021"),
) -> None:
    metrics = (
        ("annual_return", "Annual return", ".1%"),
        ("annual_volatility", "Annual volatility", ".1%"),
        ("sharpe", "Sharpe ratio", ".2f"),
    )
    deciles = list(range(1, 11))
    profiles = {}
    for row in rows(report / "deciles_summary.csv"):
        decile = int(row["decile"])
        if decile in deciles:
            key = (row["period"], row["model"], decile)
            if key in profiles:
                raise ValueError(f"Duplicate decile result for {key}")
            profiles[key] = row
    chart = {
        "kind": "decile-profiles",
        "deciles": deciles,
        "series": [
            {"id": model, "label": label, "role": role} for model, label, role in models
        ],
        "metrics": [
            {"id": metric, "label": label, "format": unit}
            for metric, label, unit in metrics
        ],
        "periods": [
            {
                "label": period,
                "values": {
                    model: {
                        metric: [
                            float(profiles[period, model, decile][metric])
                            for decile in deciles
                        ]
                        for metric, _, _ in metrics
                    }
                    for model, *_ in models
                },
            }
            for period in periods
        ],
    }

    pairs = {}
    for row in rows(report / "correlations.csv"):
        if row["period"] == periods[0]:
            pair = frozenset(row["pair"].split("|"))
            if pair in pairs:
                raise ValueError(f"Duplicate model correlation for {pair}")
            pairs[pair] = row
    matrices = []
    for column, title in (("score_rho", "Score rankings"), ("pnl_rho", "Net returns")):
        values = []
        for index, (model, *_) in enumerate(models):
            cells = []
            for other, *_ in models[:index]:
                correlation = float(pairs[frozenset((model, other))][column])
                if not math.isfinite(correlation) or abs(correlation) > 1:
                    raise ValueError(f"Invalid correlation for {model} and {other}")
                cells.append(
                    {
                        "value": correlation,
                        "display": f"{correlation:.2f}".replace("-", "−"),
                    }
                )
            values.append(cells + [None] * (len(models) - index))
        matrices.append({"title": title, "values": values})

    for destination, data in (
        (profiles_path, {"version": 1, "charts": {"profiles": chart}}),
        (
            correlations_path,
            {"labels": [label for _, label, *_ in models], "matrices": matrices},
        ),
    ):
        destination.write_text(
            json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
        )


def export_pnl(
    report: Path,
    books: Path,
    output: Path,
    *,
    models: tuple[tuple[str, str, str, str, str], ...] = (
        ("ridge", "Ridge", "equity_ridge", "#596877", "#aab3bf"),
        ("lightgbm", "LightGBM", "equity_lightgbm", "#2262ab", "#81b4f3"),
        (
            "kumo_medium",
            "Kumo Medium",
            "equity_medium",
            "#397744",
            "#a9ccaa",
        ),
    ),
    calendars: tuple[str, ...] = ("o0", "o1", "o2"),
) -> None:
    summary = next(
        row
        for row in rows(report / "books.csv")
        if (row["period"], row["model"], row["basis"])
        == ("1999–2021", "ridge", "long_short_net")
    )
    start = date.fromisoformat(summary["first_date"])
    end = date.fromisoformat(summary["last_date"])
    opening = start - timedelta(days=1)
    dates = [opening]
    lines = []
    for model, label, role, *_ in models:
        daily = (
            pl.concat(
                pl.scan_parquet(books / model / f"returns_{calendar}.parquet")
                .filter(pl.col("date").is_between(start, end))
                .select("date", "long_short_net")
                for calendar in calendars
            )
            .group_by("date")
            .agg(
                pl.mean("long_short_net").alias("net"),
                pl.len().alias("observations"),
                pl.col("long_short_net")
                .is_finite()
                .fill_null(False)
                .all()
                .alias("valid"),
            )
            .sort("date")
            .collect()
        )
        model_dates = [opening, *daily["date"].to_list()]
        if (
            daily.height != int(summary["sessions"])
            or daily["observations"].min() != len(calendars)
            or daily["observations"].max() != len(calendars)
            or not daily["valid"].all()
            or (len(dates) > 1 and model_dates != dates)
        ):
            raise ValueError(
                f"{model} lacks a complete set of returns on the common calendar"
            )
        dates = model_dates
        lines.append(series(model, label, role, [0.0, *daily["net"]], additive=True))

    chart = {
        "kind": "performance",
        "series": [line["id"] for line in lines],
        "additive": True,
        "unit": "Net P&L per $100 of capital",
        "drawdown": True,
        "drawdownUnit": "Drawdown per $100 of capital",
        "volatilityTarget": 0.07,
        "note": "Annual P&L is mean daily net P&L × 252 on fixed capital. Sharpe uses zero cash return. Maximum drawdown is the loss per $100 of capital.",
        "zeroReference": True,
        "episodes": [
            ["1999–2011", dates[0].isoformat(), "2011-12-30"],
            ["2012–2021", "2011-12-30", dates[-1].isoformat()],
            ["2017–2021", "2016-12-30", dates[-1].isoformat()],
        ],
    }
    write_chart(
        output / "net-pnl.json",
        [day.isoformat() for day in dates],
        lines,
        {"pnl": chart},
    )

    render_pnl_fallbacks(
        output,
        dates=dates,
        portfolios=[
            (label, light, dark, [100 * total for total in accumulate(line["values"])])
            for (_, label, _, light, dark), line in zip(models, lines, strict=True)
        ],
        pnl_unit=chart["unit"],
        drawdown_unit=chart["drawdownUnit"],
    )


def render_pnl_fallbacks(
    output: Path,
    *,
    dates: list[date],
    portfolios: list[tuple[str, str, str, list[float]]],
    pnl_unit: str,
    drawdown_unit: str,
) -> None:
    for mobile in (False, True):
        for dark in (False, True):
            ink, grid = ("#e4e7ea", "#313843") if dark else ("#25313a", "#dce3ea")
            style = {"font.size": 9.5, "svg.hashsalt": "equity-model-net-pnl"}
            with plt.rc_context(style):
                figure, (equity, drawdown) = plt.subplots(
                    2,
                    1,
                    figsize=(4.25, 4.55) if mobile else (6.7, 4.55),
                    layout="constrained",
                    sharex=True,
                    height_ratios=(2, 1),
                )
                for label, light, night, pnl in portfolios:
                    color = night if dark else light
                    equity.plot(dates, pnl, label=label, color=color, linewidth=1.7)
                    loss = [
                        value - peak
                        for value, peak in zip(pnl, accumulate(pnl, max), strict=True)
                    ]
                    drawdown.plot(dates, loss, color=color, linewidth=1.1)
                for axis, title in (
                    (equity, pnl_unit),
                    (drawdown, drawdown_unit),
                ):
                    axis.set_title(title, loc="left", color=ink, fontsize=11)
                    axis.tick_params(length=0, colors=ink)
                    axis.axhline(0, color=ink, linewidth=0.6, alpha=0.6, zorder=0)
                    axis.grid(axis="y", color=grid, linewidth=0.6)
                    axis.set_axisbelow(True)
                    axis.spines[:].set_visible(False)
                drawdown.set_xlim(dates[0], dates[-1])
                drawdown.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 5))
                drawdown.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
                suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
                figure.legend(
                    loc="outside upper center",
                    ncol=3,
                    frameon=False,
                    labelcolor=ink,
                    handlelength=1.5,
                    columnspacing=1.1,
                )
                destination = output / f"net-pnl{suffix}.svg"
                figure.savefig(destination, transparent=True, metadata={"Date": None})
                plt.close(figure)
                destination.write_text(
                    "".join(
                        f"{line.rstrip()}\n"
                        for line in destination.read_text().splitlines()
                    )
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--correlations", type=Path, required=True)
    parser.add_argument("--books", type=Path, required=True)
    args = parser.parse_args()
    export(args.report, args.profiles, args.correlations)
    export_pnl(args.report, args.books, args.profiles.parent)
