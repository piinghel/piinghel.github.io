"""Render reproducible figures for the portfolio-optimization article."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import reduce
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

plt.rcParams["svg.hashsalt"] = "portfolio-optimization"


@dataclass(frozen=True)
class FigureStyle:
    background: str
    ink: str
    muted: str
    grid: str
    colors: dict[str, str]
    suffix: str = ""


@dataclass(frozen=True)
class ArticleFigureConfig:
    research_root: Path
    output_dir: Path
    review_dir: Path
    qa_dir: Path
    allocators: tuple[str, ...]
    labels: dict[str, str]
    later_period_start: date
    styles: tuple[FigureStyle, ...]


def default_figure_config() -> ArticleFigureConfig:
    """Build the article's paths, labels, and theme styles in one explicit object."""

    blog_root = Path(__file__).resolve().parents[1]
    research_root = blog_root.parent / "projects" / "portfolio_optimization"
    labels = {
        "b1_ranked_volscale": "Volatility-scaled portfolio",
        "b2_memoryless_mvo": "Standard optimizer",
        "b3_state_aware_mvo": "State-aware optimizer",
    }
    return ArticleFigureConfig(
        research_root=research_root,
        output_dir=blog_root / "assets" / "portfolio-optimization",
        review_dir=research_root / "outputs" / "review",
        qa_dir=research_root / "outputs" / "review" / "figures",
        allocators=tuple(labels),
        labels=labels,
        later_period_start=date(2022, 1, 1),
        styles=(
            FigureStyle(
                background="#ffffff",
                ink="#33404b",
                muted="#6a7883",
                grid="#dbe1e3",
                colors={
                    "b1_ranked_volscale": "#a7b1b8",
                    "b2_memoryless_mvo": "#526777",
                    "b3_state_aware_mvo": "#2d7476",
                },
            ),
            FigureStyle(
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
            ),
        ),
    )


def allocator_returns(allocator: str, *, config: ArticleFigureConfig) -> pl.LazyFrame:
    """Build the equal-capital three-offset return series for one allocator."""

    calendars = []
    for offset in range(3):
        path = (
            config.research_root
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


def build_performance_data(*, config: ArticleFigureConfig) -> pl.DataFrame:
    """Align all allocators and calculate cumulative wealth and drawdown."""

    aligned = reduce(
        lambda left, right: left.join(right, on="date", how="inner"),
        [
            allocator_returns(allocator, config=config)
            for allocator in config.allocators
        ],
    )
    data = (
        aligned.sort("date")
        .with_columns(
            ((pl.col(allocator) + 1.0).cum_prod()).alias(f"{allocator}_wealth")
            for allocator in config.allocators
        )
        .with_columns(
            (
                pl.col(f"{allocator}_wealth") / pl.col(f"{allocator}_wealth").cum_max()
                - 1.0
            ).alias(f"{allocator}_drawdown")
            for allocator in config.allocators
        )
        .collect()
    )
    validate_performance_data(data, allocators=config.allocators)
    return data


def validate_performance_data(
    data: pl.DataFrame, *, allocators: tuple[str, ...]
) -> None:
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

    if tuple(expected) != allocators:
        raise ValueError(
            "figure allocator order differs from the audited specification"
        )
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
    axis.tick_params(axis="both", colors=style.muted, length=0, labelsize=10.0)
    axis.grid(axis="y", color=style.grid, linewidth=0.8, alpha=0.75)
    axis.grid(False, axis="x")


def save_svg(fig: plt.Figure, target: Path, style: FigureStyle) -> None:
    """Save deterministic, whitespace-normalized article SVG."""

    fig.savefig(
        target,
        format="svg",
        facecolor=style.background,
        metadata={"Date": None},
    )
    svg = target.read_text(encoding="utf-8")
    target.write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
    )


def plot_performance(
    data: pl.DataFrame,
    style: FigureStyle,
    *,
    config: ArticleFigureConfig,
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
            config.later_period_start,
            color=style.muted,
            linewidth=0.9,
            linestyle=(0, (2, 3)),
        )

    dates = data["date"].to_numpy()
    for allocator in config.allocators:
        width = 2.2 if allocator == "b3_state_aware_mvo" else 1.55
        color = style.colors[allocator]
        wealth = data[f"{allocator}_wealth"].to_numpy()
        drawdown = data[f"{allocator}_drawdown"].to_numpy() * 100
        wealth_axis.plot(
            dates,
            wealth,
            color=color,
            linewidth=width,
            label=config.labels[allocator],
        )
        drawdown_axis.plot(
            dates,
            drawdown,
            color=color,
            linewidth=max(1.25, width - 0.25),
            zorder=2,
        )

    wealth_axis.set_yscale("log")
    wealth_axis.set_ylabel("Growth of $1 (log scale)", color=style.muted, fontsize=11.0)
    wealth_axis.yaxis.set_major_locator(FixedLocator([1, 2, 4, 8, 16]))
    wealth_axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}×"))
    wealth_axis.yaxis.set_minor_formatter(NullFormatter())
    wealth_axis.legend(
        loc="upper left",
        ncol=1 if mobile else 3,
        frameon=False,
        labelcolor=style.ink,
        fontsize=10.0,
        borderaxespad=0,
        handlelength=2.3,
        columnspacing=1.6,
    )

    drawdown_axis.set_ylabel("Drawdown (%)", color=style.muted, fontsize=11.0)
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
    target = config.output_dir / f"performance-and-drawdowns{suffix}{style.suffix}.svg"
    save_svg(fig, target, style)
    config.qa_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        config.qa_dir / f"performance-and-drawdowns{suffix}{style.suffix}.png",
        dpi=180,
        facecolor=style.background,
    )
    plt.close(fig)


def build_risk_figure_data(
    *, config: ArticleFigureConfig
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Load per-rebalance risk forecasts and the rolling-beta diagnostic."""

    risk_scan = pl.scan_csv(
        config.review_dir / "risk_calibration_by_rebalance.csv",
        try_parse_dates=True,
        infer_schema_length=None,
    )
    expected_risk_columns = {
        "allocator",
        "offset",
        "execution_date",
        "execution_predicted_annual_volatility",
        "realised_annual_volatility",
        "failure_status",
    }
    if not expected_risk_columns.issubset(risk_scan.collect_schema().names()):
        raise ValueError("per-rebalance risk evidence has an unexpected schema")
    risk = (
        risk_scan.filter(pl.col("failure_status") == "ok")
        .select(
            "allocator",
            "offset",
            "execution_date",
            (pl.col("execution_predicted_annual_volatility") * 100).alias(
                "predicted_volatility_pct"
            ),
            (pl.col("realised_annual_volatility") * 100).alias(
                "realised_volatility_pct"
            ),
        )
        .sort("allocator", "offset", "execution_date")
        .collect()
    )
    risk_counts = risk.lazy().group_by("allocator").len().collect()
    if set(risk_counts.get_column("allocator")) != set(config.allocators):
        raise ValueError("per-rebalance risk evidence is missing an allocator")
    if set(risk_counts.get_column("len")) != {1_444}:
        raise ValueError("expected 1,444 risk observations per allocator")
    if risk.get_column("offset").n_unique() != 3:
        raise ValueError("risk evidence must contain all three rebalance schedules")

    rolling_scan = pl.scan_csv(
        config.review_dir / "rolling_realised_beta_252d.csv",
        try_parse_dates=True,
        infer_schema_length=None,
    )
    if "offset" not in rolling_scan.collect_schema().names():
        raise ValueError("rolling-beta evidence has an unexpected schema")
    rolling_mean = (
        rolling_scan.group_by(
            "allocator", "allocator_label", "date", maintain_order=True
        )
        .agg(pl.col("realised_beta_252d").mean())
        .sort("allocator", "date")
        .with_columns(pl.col("date").dt.truncate("1mo").alias("_month"))
        .group_by("allocator", "allocator_label", "_month", maintain_order=True)
        .agg(
            pl.col("date").last(),
            pl.col("realised_beta_252d").last(),
        )
        .drop("_month")
        .sort("allocator", "date")
        .collect()
    )
    if set(rolling_mean.get_column("allocator")) != set(config.allocators):
        raise ValueError("rolling-beta evidence is missing an allocator")
    return risk, rolling_mean


def plot_risk_forecasts(
    risk: pl.DataFrame,
    style: FigureStyle,
    *,
    config: ArticleFigureConfig,
    mobile: bool,
) -> None:
    """Plot forecast and subsequent realised volatility at every rebalance."""

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(4.6, 8.8) if mobile else (10.8, 7.6),
        facecolor=style.background,
        sharex=True,
        sharey=True,
        gridspec_kw={"hspace": 0.20},
    )
    for axis in axes:
        style_axis(axis, style)
        axis.set_ylim(0, 20)
        axis.yaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20]))

    short_labels = {
        "b1_ranked_volscale": "Volatility-scaled portfolio",
        "b2_memoryless_mvo": "Standard optimizer",
        "b3_state_aware_mvo": "State-aware optimizer",
    }
    realised_color = style.colors["b3_state_aware_mvo"]
    for axis, allocator in zip(axes, config.allocators, strict=True):
        allocator_frame = risk.filter(pl.col("allocator") == allocator)
        for offset in ("o0", "o1", "o2"):
            frame = allocator_frame.filter(pl.col("offset") == offset).sort(
                "execution_date"
            )
            dates = frame.get_column("execution_date").to_numpy()
            axis.plot(
                dates,
                frame.get_column("predicted_volatility_pct").to_numpy(),
                color=style.muted,
                linewidth=0.9,
                alpha=0.80,
                linestyle=(0, (3, 2)),
                zorder=2,
            )
            axis.plot(
                dates,
                frame.get_column("realised_volatility_pct").to_numpy(),
                color=realised_color,
                linewidth=0.9,
                alpha=0.52,
                zorder=3,
            )
            overflow = frame.filter(pl.col("realised_volatility_pct") > 20)
            axis.scatter(
                overflow.get_column("execution_date").to_numpy(),
                np.full(overflow.height, 19.55),
                color=realised_color,
                marker="^",
                s=18 if mobile else 20,
                linewidths=0,
                alpha=0.86,
                clip_on=True,
                zorder=4,
            )
        axis.set_title(
            short_labels[allocator],
            loc="left",
            color=style.ink,
            fontsize=10.2 if mobile else 10.8,
            pad=5,
        )

    date_min = risk.get_column("execution_date").min()
    date_max = risk.get_column("execution_date").max()
    axes[-1].set_xlim(date_min, date_max)
    axes[-1].xaxis.set_major_locator(mdates.YearLocator(7 if mobile else 5))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[1].set_ylabel(
        "Annualised volatility (%)", color=style.muted, fontsize=10.5
    )
    legend_handles = [
        Line2D(
            [0],
            [0],
            color=style.muted,
            linewidth=1.4,
            linestyle=(0, (3, 2)),
            label="Predicted at rebalance",
        ),
        Line2D(
            [0],
            [0],
            color=realised_color,
            linewidth=1.5,
            label="Realised over next holding period",
        ),
        Line2D(
            [0],
            [0],
            color=realised_color,
            marker="^",
            markersize=5.5,
            linewidth=0,
            label="Realised above 20%",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.53, 0.995),
        ncol=1 if mobile else 3,
        frameon=False,
        labelcolor=style.ink,
        fontsize=9.4 if mobile else 10.0,
        handlelength=2.6,
        columnspacing=1.8,
    )
    fig.subplots_adjust(
        left=0.19 if mobile else 0.10,
        right=0.98,
        top=0.89 if mobile else 0.90,
        bottom=0.07 if mobile else 0.08,
    )
    suffix = "-mobile" if mobile else ""
    target = config.output_dir / f"risk-forecast-through-time{suffix}{style.suffix}.svg"
    save_svg(fig, target, style)
    config.qa_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        config.qa_dir / f"risk-forecast-through-time{suffix}{style.suffix}.png",
        dpi=180,
        facecolor=style.background,
    )
    plt.close(fig)


def plot_realised_beta(
    rolling_beta: pl.DataFrame,
    style: FigureStyle,
    *,
    config: ArticleFigureConfig,
    mobile: bool,
) -> None:
    """Plot rolling realised beta without endpoint labels or future whitespace."""

    fig, axis = plt.subplots(
        1,
        1,
        figsize=(4.6, 5.6) if mobile else (10.8, 4.8),
        facecolor=style.background,
    )
    style_axis(axis, style)
    axis.axhspan(-0.05, 0.05, color=style.muted, alpha=0.14, linewidth=0)
    axis.axhline(0.0, color=style.muted, linewidth=0.8, alpha=0.75)
    line_styles = {
        "b1_ranked_volscale": (0, (1.5, 2.0)),
        "b2_memoryless_mvo": (0, (4.0, 2.0)),
        "b3_state_aware_mvo": "solid",
    }
    for allocator in config.allocators:
        frame = rolling_beta.filter(pl.col("allocator") == allocator).sort("date")
        dates = frame.get_column("date").to_numpy()
        values = frame.get_column("realised_beta_252d").to_numpy()
        width = 2.0 if allocator == "b3_state_aware_mvo" else 1.35
        axis.plot(
            dates,
            values,
            color=style.colors[allocator],
            linewidth=width,
            linestyle=line_styles[allocator],
            label=config.labels[allocator],
            zorder=2,
        )
    axis.set_ylim(-0.20, 0.42)
    axis.yaxis.set_major_locator(FixedLocator([-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]))
    axis.set_xlim(
        rolling_beta.get_column("date").min(),
        rolling_beta.get_column("date").max(),
    )
    axis.set_ylabel("252-day realised beta", color=style.muted, fontsize=10.5)
    tick_years = (
        (2000, 2006, 2012, 2018, 2024)
        if mobile
        else (2000, 2005, 2010, 2015, 2020, 2025)
    )
    axis.xaxis.set_major_locator(
        FixedLocator([mdates.date2num(date(year, 1, 1)) for year in tick_years])
    )
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axis.legend(
        loc="lower left",
        bbox_to_anchor=(0.0, 1.02),
        ncol=1 if mobile else 3,
        frameon=False,
        labelcolor=style.ink,
        fontsize=9.3 if mobile else 10.0,
        borderaxespad=0,
        handlelength=2.5,
        columnspacing=1.6,
    )
    fig.subplots_adjust(
        left=0.19 if mobile else 0.09,
        right=0.98,
        top=0.78 if mobile else 0.88,
        bottom=0.10 if mobile else 0.14,
    )
    suffix = "-mobile" if mobile else ""
    target = config.output_dir / f"realised-beta{suffix}{style.suffix}.svg"
    save_svg(fig, target, style)
    config.qa_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        config.qa_dir / f"realised-beta{suffix}{style.suffix}.png",
        dpi=180,
        facecolor=style.background,
    )
    plt.close(fig)


def write_risk_figure_metadata(*, config: ArticleFigureConfig) -> None:
    """Persist the caption and source-to-asset manifest beside the evidence."""

    risk_caption = (
        "Predicted and subsequently realised annualised volatility at every "
        "rebalance. Each panel contains the three staggered schedules. Forecasts "
        "are measured at execution; realised volatility covers the subsequent "
        "execution-to-next-execution holding period. The common 0–20% scale marks "
        "higher observations with triangles; the counts are 10, 12, and 11 and "
        "the maxima are 48.9%, 34.7%, and 34.3%. B1 is evaluated with B2's "
        "covariance model as a common-model diagnostic."
    )
    beta_caption = (
        "252-day realised market beta, sampled monthly and averaged across the "
        "three staggered schedules. The grey ±0.05 band is the target range for "
        "the standard and state-aware portfolios, not a guarantee for realised beta."
    )
    (config.review_dir / "risk_calibration_figure_caption.md").write_text(
        risk_caption + "\n\n" + beta_caption + "\n", encoding="utf-8"
    )
    manifest = {
        "displays": [
            "risk_forecast_through_time",
            "realised_beta_through_time",
        ],
        "questions": [
            "At each rebalance, does predicted risk track risk over the next holding period?",
            "Does realised market exposure stay controlled through time?",
        ],
        "evidence": [
            "outputs/review/risk_calibration_by_rebalance.csv",
            "outputs/review/rolling_realised_beta_252d.csv",
        ],
        "article_assets": [
            "assets/portfolio-optimization/risk-forecast-through-time.svg",
            "assets/portfolio-optimization/risk-forecast-through-time_dark.svg",
            "assets/portfolio-optimization/risk-forecast-through-time-mobile.svg",
            "assets/portfolio-optimization/risk-forecast-through-time-mobile_dark.svg",
            "assets/portfolio-optimization/realised-beta.svg",
            "assets/portfolio-optimization/realised-beta_dark.svg",
            "assets/portfolio-optimization/realised-beta-mobile.svg",
            "assets/portfolio-optimization/realised-beta-mobile_dark.svg",
        ],
        "captions": {
            "risk_forecast_through_time": risk_caption,
            "realised_beta_through_time": beta_caption,
        },
        "visual_choices": {
            "risk_forecast": (
                "three allocator panels on a shared zero-based scale; all 1,444 "
                "rebalance observations per allocator retained; one line per schedule; "
                "values above the 20% display range marked at the boundary and "
                "reported exactly in the caption"
            ),
            "beta": (
                "252-day realised beta, mean across offsets, sampled monthly for display"
            ),
            "target_band": ("neutral grey; applies only to B2/B3 target portfolios"),
            "excluded_from_main_figure": [
                "QLIKE chart",
                "realised-to-predicted ratio chart",
                "target-versus-realised beta chart",
                "rolling-correlation chart",
            ],
        },
    }
    (config.review_dir / "risk_calibration_figure_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    config = default_figure_config()
    config.output_dir.mkdir(parents=True, exist_ok=True)
    data = build_performance_data(config=config)
    risk, rolling_beta = build_risk_figure_data(config=config)
    for style in config.styles:
        for mobile in (False, True):
            plot_performance(data, style, config=config, mobile=mobile)
            plot_risk_forecasts(risk, style, config=config, mobile=mobile)
            plot_realised_beta(
                rolling_beta, style, config=config, mobile=mobile
            )
    write_risk_figure_metadata(config=config)
    print(
        "Rendered twelve SVGs from "
        f"{data.height:,} common-date observations ({data['date'].min()} to "
        f"{data['date'].max()}) and {risk.height:,} per-rebalance risk observations."
    )


if __name__ == "__main__":
    main()
