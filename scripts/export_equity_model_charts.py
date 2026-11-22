"""Export the stock-ranking article's aggregate charts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from bisect import bisect_left
from datetime import date, timedelta
from itertools import accumulate
from pathlib import Path
from statistics import stdev

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import polars as pl
from blog_charts import series, write_chart
from figure_svg import save_svg, svg_path


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

    export_rank(report, profiles_path.parent, models=models, periods=periods)


def export_rank(
    report: Path,
    output: Path,
    *,
    models: tuple[tuple[str, str, str], ...],
    periods: tuple[str, ...],
) -> None:
    metrics = (
        ("ic_mean", "Rank IC", 4),
        ("ic_sd", "IC SD", 3),
        ("icir", "ICIR", 3),
    )
    rank_rows = {}
    for row in rows(report / "rank_summary.csv"):
        key = (row["period"], row["model"])
        if key in rank_rows:
            raise ValueError(f"Duplicate rank result for {key}")
        rank_rows[key] = row

    period_data = []
    for period in periods:
        results = {model: rank_rows[period, model] for model, *_ in models}
        dates = {int(result["dates"]) for result in results.values()}
        if len(dates) != 1:
            raise ValueError(f"Models use different signal date counts in {period}")
        period_data.append({
            "label": period,
            "dates": dates.pop(),
            "values": {
                model: {metric: float(result[metric]) for metric, *_ in metrics}
                for model, result in results.items()
            },
        })

    panels = []
    for metric, label, digits in metrics:
        all_values = [
            period["values"][model][metric]
            for period in period_data
            for model, *_ in models
        ]
        spacing = 0.5 * 10 ** math.floor(math.log10(max(map(abs, all_values)) or 1))
        lower = round(min(0, math.floor(min(all_values) / spacing) * spacing), digits)
        upper = round(max(spacing, math.ceil(max(all_values) / spacing) * spacing), digits)
        metric_info = {"id": metric, "label": label, "digits": digits, "domain": [lower, upper]}
        panels.append((metric_info, [period_data[0]["values"][model][metric] for model, *_ in models]))

    chart = {
        "kind": "rank-bars",
        "series": [
            {"id": model, "label": label, "role": role} for model, label, role in models
        ],
        "metrics": [metric for metric, _ in panels],
        "periods": period_data,
    }
    base = output / "rank-metrics"
    base.with_suffix(".json").write_text(
        json.dumps({"version": 1, "charts": {"rank": chart}}, ensure_ascii=False,
                   allow_nan=False, indent=2) + "\n"
    )
    render_rank_fallbacks(
        base,
        labels=[label for _, label, _ in models],
        is_kumo=[model.startswith("kumo_") for model, _, _ in models],
        panels=panels,
    )


def render_rank_fallbacks(
    base: Path,
    *,
    labels: list[str],
    is_kumo: list[bool],
    panels: list[tuple[dict, list[float]]],
) -> None:
    for mobile in (False, True):
        for dark in (False, True):
            ink, rule = ("#dce3eb", "#52606d") if dark else ("#27343d", "#bcc4cb")
            accent = "#83a7bc" if dark else "#63849a"
            colors = [accent if model else "#83909b" for model in is_kumo]
            text_size = 9 if mobile else 9.5
            with plt.rc_context({"svg.hashsalt": "stock-rank-metrics", "font.size": text_size}):
                figure, axes = plt.subplots(
                    len(panels) if mobile else 1,
                    1 if mobile else len(panels),
                    figsize=(4.1, 6.3) if mobile else (7.6, 2.65),
                    sharey=True,
                    layout="constrained",
                )
                for index, (axis, (metric, values)) in enumerate(zip(axes, panels, strict=True)):
                    lower, upper = metric["domain"]
                    span = upper - lower
                    axis.axvline(0, linewidth=0.8, color=rule, zorder=0)
                    axis.barh(labels, values, height=0.41, color=colors)
                    axis.set_title(metric["label"], loc="left", color=ink, fontsize=text_size, pad=8)
                    for label_row, value in zip(labels, values, strict=True):
                        number = f"{value:.{metric['digits']}f}".replace("-", "−")
                        axis.text(1, label_row, number, ha="right", va="center",
                                  color=ink, transform=axis.get_yaxis_transform())
                    axis.set_xlim(lower, upper + span * (0.24 if mobile else 0.36))
                    axis.set_ylim(len(labels) - 0.55, -0.55)
                    axis.set_xticks([0, upper], ["0", f"{upper:g}"])
                    axis.tick_params(axis="y", labelleft=mobile or index == 0, pad=8)
                    axis.tick_params(length=0, colors=ink)
                    axis.spines[:].set_visible(False)
                save_svg(figure, svg_path(base, mobile=mobile, dark=dark), transparent=True)


def export_pnl(
    report: Path,
    books: Path,
    output: Path,
    *,
    models: tuple[tuple[str, str, str, str, str], ...] = (
        ("ridge", "Ridge", "equity_ridge", "#596877", "#aab3bf"),
        ("lightgbm", "LightGBM", "equity_lightgbm", "#2262ab", "#81b4f3"),
        ("kumo_small", "Small 6w", "equity_small_six", "#5c55a3", "#b9b0fa"),
        (
            "kumo_medium",
            "Kumo Medium",
            "equity_medium",
            "#397744",
            "#a9ccaa",
        ),
        ("kumo_small_roll3", "Small rolling", "equity_rolling", "#9c3d58", "#e3a2b3"),
    ),
    periods: tuple[str, ...] = ("1999–2021", "1999–2011", "2012–2021", "2017–2021"),
    initially_hidden: tuple[str, ...] = ("kumo_small_roll3",),
    calendars: tuple[str, ...] = ("o0", "o1", "o2"),
    volatility_target: float = 0.07,
    annualization: int = 252,
) -> None:
    summaries = {
        row["period"]: row
        for row in rows(report / "books.csv")
        if (row["model"], row["basis"]) == (models[0][0], "long_short_net")
    }
    summary = summaries[periods[0]]
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
        lines.append(
            series(
                model, label, role, [0.0, *daily["net"]], additive=True,
                visible=model not in initially_hidden,
            )
        )

    episodes = []
    for period in periods[1:]:
        period_summary = summaries[period]
        period_start = date.fromisoformat(period_summary["first_date"])
        prior_close = dates[bisect_left(dates, period_start) - 1]
        episodes.append([period, prior_close.isoformat(), period_summary["last_date"]])

    chart = {
        "kind": "performance",
        "series": [line["id"] for line in lines],
        "additive": True,
        "unit": "Cumulative net P&L (% of fixed capital)",
        "drawdown": True,
        "drawdownUnit": "Drawdown (% of fixed capital)",
        "volatilityTarget": volatility_target,
        "matchVolatilityByDefault": True,
        "note": f"Annual P&L is mean daily net P&L × {annualization}. P&L and drawdown are percentages of fixed capital. Sharpe uses zero cash return.",
        "zeroReference": True,
        "episodes": episodes,
    }
    write_chart(
        output / "net-pnl.json",
        [day.isoformat() for day in dates],
        lines,
        {"pnl": chart},
        annualization=annualization,
    )

    portfolios = []
    for (_, label, _, light, dark), line in zip(models, lines, strict=True):
        if not line["visible"]:
            continue
        realized_volatility = stdev(line["values"][1:]) * math.sqrt(annualization)
        multiplier = 100 * volatility_target / realized_volatility
        pnl = [multiplier * total for total in accumulate(line["values"])]
        portfolios.append((label, light, dark, pnl))

    render_pnl_fallbacks(
        output,
        dates=dates,
        portfolios=portfolios,
        pnl_unit=f"Net P&L (% of capital) at {volatility_target * 100:g}% volatility",
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
                figure.legend(
                    loc="outside upper center",
                    ncol=2 if mobile else min(4, len(portfolios)),
                    frameon=False,
                    labelcolor=ink,
                    handlelength=1.5,
                    columnspacing=1.1,
                )
                destination = svg_path(output / "net-pnl", mobile=mobile, dark=dark)
                save_svg(figure, destination, transparent=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--correlations", type=Path, required=True)
    parser.add_argument("--books", type=Path, required=True)
    parser.add_argument("--period", action="append", help="Report periods, full history first")
    args = parser.parse_args()
    options = {"periods": tuple(args.period)} if args.period else {}
    export(args.report, args.profiles, args.correlations, **options)
    export_pnl(args.report, args.books, args.profiles.parent, **options)
