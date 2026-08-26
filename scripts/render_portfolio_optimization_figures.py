"""Render the portfolio-optimization article's performance figure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import reduce
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

BLOG_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = BLOG_ROOT.parent / "projects" / "portfolio_optimization"
OUTPUT_DIR = BLOG_ROOT / "assets" / "portfolio-optimization"

ALLOCATORS = (
    "b1_ranked_volscale",
    "b2_memoryless_mvo",
    "b3_state_aware_mvo",
)
LABELS = {
    "b1_ranked_volscale": "Volatility-scaled portfolio",
    "b2_memoryless_mvo": "Standard optimizer",
    "b3_state_aware_mvo": "State-aware optimizer",
}
LATER_PERIOD_START = date(2022, 1, 1)


@dataclass(frozen=True)
class FigureStyle:
    background: str
    ink: str
    muted: str
    grid: str
    colors: dict[str, str]
    suffix: str = ""


LIGHT = FigureStyle(
    background="#ffffff",
    ink="#33404b",
    muted="#6a7883",
    grid="#dbe1e3",
    colors={
        "b1_ranked_volscale": "#a7b1b8",
        "b2_memoryless_mvo": "#526777",
        "b3_state_aware_mvo": "#2d7476",
    },
)
DARK = FigureStyle(
    background="#0d1117",
    ink="#c9d1d9",
    muted="#8b949e",
    grid="#30363d",
    colors={
        "b1_ranked_volscale": "#8b949e",
        "b2_memoryless_mvo": "#91a4b5",
        "b3_state_aware_mvo": "#55a6a8",
    },
    suffix="_dark",
)


def allocator_returns(allocator: str) -> pl.LazyFrame:
    """Build the equal-capital three-offset return series for one allocator."""

    calendars = []
    for offset in range(3):
        path = (
            RESEARCH_ROOT
            / "outputs"
            / "full"
            / allocator
            / "backtest"
            / "calendars"
            / f"o{offset}"
            / "returns.csv"
        )
        calendars.append(
            pl.scan_csv(path, try_parse_dates=True).select(
                "date",
                pl.col("long_short_net").alias(f"offset_{offset}"),
            )
        )

    return (
        reduce(lambda left, right: left.join(right, on="date", how="inner"), calendars)
        .with_columns(
            pl.mean_horizontal("offset_0", "offset_1", "offset_2").alias(allocator)
        )
        .select("date", allocator)
    )


def build_performance_data() -> pl.DataFrame:
    """Align all allocators and calculate cumulative wealth and drawdown."""

    aligned = reduce(
        lambda left, right: left.join(right, on="date", how="inner"),
        [allocator_returns(allocator) for allocator in ALLOCATORS],
    )
    data = (
        aligned.sort("date")
        .with_columns(
            ((pl.col(allocator) + 1.0).cum_prod()).alias(f"{allocator}_wealth")
            for allocator in ALLOCATORS
        )
        .with_columns(
            (
                pl.col(f"{allocator}_wealth") / pl.col(f"{allocator}_wealth").cum_max()
                - 1.0
            ).alias(f"{allocator}_drawdown")
            for allocator in ALLOCATORS
        )
        .collect()
    )
    validate_performance_data(data)
    return data


def validate_performance_data(data: pl.DataFrame) -> None:
    """Fail if the article series no longer matches the audited run."""

    expected = {
        "b1_ranked_volscale": (8.70, 1.12, 18.93),
        "b2_memoryless_mvo": (10.84, 1.37, 18.10),
        "b3_state_aware_mvo": (11.67, 1.44, 15.53),
    }
    if data.height != 6_963 or data["date"].min().isoformat() != "1998-09-22":
        raise ValueError("unexpected common performance window")
    if data["date"].max().isoformat() != "2026-05-27":
        raise ValueError("unexpected performance end date")
    if data.null_count().sum_horizontal()[0] != 0:
        raise ValueError("performance series contains nulls")

    for allocator, (
        expected_return,
        expected_sharpe,
        expected_drawdown,
    ) in expected.items():
        returns = data[allocator]
        annual_return = ((returns + 1.0).product() ** (252 / data.height) - 1.0) * 100
        sharpe = returns.mean() / returns.std() * np.sqrt(252)
        drawdown = -data[f"{allocator}_drawdown"].min() * 100
        observed = np.array([annual_return, sharpe, drawdown])
        target = np.array([expected_return, expected_sharpe, expected_drawdown])
        if not np.allclose(observed, target, atol=0.015):
            raise ValueError(
                f"{allocator} no longer matches audited metrics: {observed.tolist()}"
            )


def style_axis(axis: plt.Axes, style: FigureStyle) -> None:
    axis.set_facecolor(style.background)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color(style.grid)
    axis.tick_params(axis="both", colors=style.muted, length=0, labelsize=9.2)
    axis.grid(axis="y", color=style.grid, linewidth=0.8, alpha=0.75)
    axis.grid(False, axis="x")


def plot_performance(
    data: pl.DataFrame,
    style: FigureStyle,
    *,
    mobile: bool,
) -> None:
    size = (4.6, 7.2) if mobile else (10.8, 6.7)
    fig, (wealth_axis, drawdown_axis) = plt.subplots(
        2,
        1,
        figsize=size,
        facecolor=style.background,
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.05},
    )
    for axis in (wealth_axis, drawdown_axis):
        style_axis(axis, style)
        axis.axvline(
            LATER_PERIOD_START,
            color=style.muted,
            linewidth=0.9,
            linestyle=(0, (2, 3)),
        )

    event_x = mdates.date2num(LATER_PERIOD_START)
    wealth_axis.annotate(
        "Later period\nstarts in 2022",
        xy=(event_x, 0.97),
        xycoords=wealth_axis.get_xaxis_transform(),
        xytext=(-8, 0),
        textcoords="offset points",
        color=style.muted,
        fontsize=8.2 if mobile else 8.8,
        ha="right",
        va="top",
        bbox={
            "boxstyle": "square,pad=0.12",
            "facecolor": style.background,
            "edgecolor": "none",
            "alpha": 0.96,
        },
        zorder=5,
    )

    dates = data["date"].to_numpy()
    for allocator in ALLOCATORS:
        width = 2.2 if allocator == "b3_state_aware_mvo" else 1.55
        color = style.colors[allocator]
        wealth = data[f"{allocator}_wealth"].to_numpy()
        drawdown = data[f"{allocator}_drawdown"].to_numpy() * 100
        wealth_axis.plot(
            dates,
            wealth,
            color=color,
            linewidth=width,
            label=LABELS[allocator],
        )
        drawdown_axis.plot(
            dates,
            drawdown,
            color=color,
            linewidth=max(1.25, width - 0.25),
            zorder=2,
        )

    wealth_axis.set_yscale("log")
    wealth_axis.set_ylabel("Growth of $1 (log scale)", color=style.muted, fontsize=10.5)
    wealth_axis.yaxis.set_major_locator(FixedLocator([1, 2, 4, 8, 16]))
    wealth_axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}×"))
    wealth_axis.yaxis.set_minor_formatter(NullFormatter())
    wealth_axis.legend(
        loc="upper left",
        ncol=1 if mobile else 3,
        frameon=False,
        labelcolor=style.ink,
        fontsize=9.3,
        borderaxespad=0,
        handlelength=2.3,
        columnspacing=1.6,
    )

    drawdown_axis.set_ylabel("Drawdown (%)", color=style.muted, fontsize=10.5)
    drawdown_axis.set_ylim(-21, 1)
    drawdown_axis.yaxis.set_major_locator(FixedLocator([-20, -10, 0]))
    drawdown_axis.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 4))
    drawdown_axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    drawdown_axis.set_xlim(dates[0], dates[-1])

    fig.subplots_adjust(
        left=0.18 if mobile else 0.10,
        right=0.98,
        top=0.98,
        bottom=0.08,
    )
    suffix = "-mobile" if mobile else ""
    target = OUTPUT_DIR / f"performance-and-drawdowns{suffix}{style.suffix}.svg"
    fig.savefig(target, format="svg", facecolor=style.background)
    svg = target.read_text(encoding="utf-8")
    target.write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build_performance_data()
    for style in (LIGHT, DARK):
        for mobile in (False, True):
            plot_performance(data, style, mobile=mobile)
    print(
        "Rendered four SVGs from "
        f"{data.height:,} common-date observations ({data['date'].min()} to "
        f"{data['date'].max()})."
    )


if __name__ == "__main__":
    main()
