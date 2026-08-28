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
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter


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
    axis.tick_params(axis="both", colors=style.muted, length=0, labelsize=9.2)
    axis.grid(axis="y", color=style.grid, linewidth=0.8, alpha=0.75)
    axis.grid(False, axis="x")


def save_svg(fig: plt.Figure, target: Path, style: FigureStyle) -> None:
    """Save deterministic, whitespace-normalized article SVG."""

    fig.savefig(target, format="svg", facecolor=style.background)
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
    plt.close(fig)


def build_risk_figure_data(
    *, config: ArticleFigureConfig
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Load and validate the compact evidence produced by Work package 1."""

    calibration = pl.read_csv(
        config.review_dir / "risk_calibration_points.csv", infer_schema_length=None
    )
    rolling = pl.read_csv(
        config.review_dir / "rolling_realised_beta_252d.csv",
        try_parse_dates=True,
        infer_schema_length=None,
    )
    expected_calibration = {
        "allocator",
        "root_mean_predicted_annual_variance",
        "root_mean_realised_annual_variance",
    }
    if not expected_calibration.issubset(calibration.columns):
        raise ValueError("risk calibration evidence has an unexpected schema")
    if calibration.height != 3:
        raise ValueError(
            f"expected one calibration point per allocator, found {calibration.height}"
        )
    if set(calibration.get_column("allocator").unique()) != set(config.allocators):
        raise ValueError("risk calibration evidence is missing an allocator")
    if rolling.get_column("offset").n_unique() != 3:
        raise ValueError("rolling-beta evidence must contain all three offsets")
    rolling_mean = (
        rolling.group_by("allocator", "allocator_label", "date", maintain_order=True)
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
    )
    return calibration, rolling_mean


def plot_risk_calibration_and_beta(
    calibration: pl.DataFrame,
    rolling_beta: pl.DataFrame,
    style: FigureStyle,
    *,
    config: ArticleFigureConfig,
    mobile: bool,
) -> None:
    """One compact figure: calibration on the left, realised beta on the right."""

    if mobile:
        fig, axes = plt.subplots(
            2,
            1,
            figsize=(4.6, 7.8),
            facecolor=style.background,
            gridspec_kw={"height_ratios": [1.0, 1.12], "hspace": 0.20},
        )
    else:
        fig, axes = plt.subplots(
            1,
            2,
            figsize=(10.8, 4.8),
            facecolor=style.background,
            gridspec_kw={"width_ratios": [0.92, 1.28], "wspace": 0.25},
        )
    calibration_axis, beta_axis = axes
    for axis in axes:
        style_axis(axis, style)

    lower, upper = 0.04, 0.10
    calibration_axis.plot(
        [lower, upper],
        [lower, upper],
        color=style.muted,
        linewidth=1.0,
        linestyle=(0, (3, 3)),
        zorder=1,
    )
    calibration_axis.text(
        0.096,
        0.044,
        "45° = match",
        color=style.muted,
        fontsize=8.0,
        rotation=0,
        ha="right",
        va="center",
    )
    calibration_label_offsets = {
        "b1_ranked_volscale": (0.045, 0.079),
        "b2_memoryless_mvo": (0.078, 0.092),
        "b3_state_aware_mvo": (0.078, 0.080),
    }
    short_labels = {
        "b1_ranked_volscale": "Vol-scaled",
        "b2_memoryless_mvo": "Standard",
        "b3_state_aware_mvo": "State-aware",
    }
    for allocator in config.allocators:
        frame = calibration.filter(pl.col("allocator") == allocator)
        x = frame.get_column("root_mean_predicted_annual_variance").to_numpy()
        y = frame.get_column("root_mean_realised_annual_variance").to_numpy()
        marker = "s" if allocator == "b2_memoryless_mvo" else "o"
        size = 72 if allocator == "b2_memoryless_mvo" else 42
        facecolor = (
            "none" if allocator == "b2_memoryless_mvo" else style.colors[allocator]
        )
        calibration_axis.scatter(
            x,
            y,
            edgecolors=style.colors[allocator],
            facecolors=facecolor,
            marker=marker,
            s=size,
            linewidths=1.5,
            zorder=2,
        )
        label_anchor = (float(x[0]), float(y[0]))
        calibration_axis.annotate(
            short_labels[allocator],
            xy=label_anchor,
            xytext=calibration_label_offsets[allocator],
            textcoords="data",
            color=style.colors[allocator],
            fontsize=8.3 if mobile else 8.8,
            ha="left",
            va="center",
            arrowprops={
                "arrowstyle": "-",
                "color": style.colors[allocator],
                "linewidth": 0.8,
                "shrinkA": 3,
                "shrinkB": 3,
            },
        )
    calibration_axis.set_xlim(lower, upper)
    calibration_axis.set_ylim(lower, upper)
    calibration_axis.set_aspect("equal", adjustable="box")
    calibration_axis.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"{value:.0%}")
    )
    calibration_axis.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"{value:.0%}")
    )
    calibration_axis.set_xlabel(
        "Predicted annualised volatility", color=style.muted, fontsize=9.5
    )
    calibration_axis.set_ylabel(
        "Realised annualised volatility", color=style.muted, fontsize=9.5
    )

    beta_axis.axhspan(-0.05, 0.05, color=style.muted, alpha=0.16, linewidth=0)
    beta_axis.axhline(0.0, color=style.muted, linewidth=0.8, alpha=0.75)
    beta_label_positions = {
        "b1_ranked_volscale": (date(2026, 10, 1), 0.055),
        "b2_memoryless_mvo": (date(2026, 10, 1), 0.090),
        "b3_state_aware_mvo": (date(2026, 10, 1), 0.020),
    }
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
        beta_axis.plot(
            dates,
            values,
            color=style.colors[allocator],
            linewidth=width,
            linestyle=line_styles[allocator],
            zorder=2,
        )
        beta_axis.annotate(
            short_labels[allocator],
            xy=(dates[-1], values[-1]),
            xytext=beta_label_positions[allocator],
            textcoords="data",
            color=style.colors[allocator],
            fontsize=8.3 if mobile else 8.8,
            ha="left",
            va="center",
            clip_on=False,
            arrowprops={
                "arrowstyle": "-",
                "color": style.colors[allocator],
                "linewidth": 0.8,
                "shrinkA": 3,
                "shrinkB": 2,
            },
        )
    beta_axis.set_ylim(-0.20, 0.42)
    beta_axis.set_xlim(date(1999, 1, 1), date(2028, 6, 1))
    beta_axis.set_ylabel("252-day realised beta", color=style.muted, fontsize=9.5)
    tick_years = (
        (2000, 2006, 2012, 2018, 2024)
        if mobile
        else (2000, 2005, 2010, 2015, 2020, 2025)
    )
    beta_axis.xaxis.set_major_locator(
        FixedLocator([mdates.date2num(date(year, 1, 1)) for year in tick_years])
    )
    beta_axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    if mobile:
        fig.subplots_adjust(left=0.19, right=0.82, top=0.98, bottom=0.07)
    else:
        fig.subplots_adjust(left=0.08, right=0.90, top=0.97, bottom=0.14)
    suffix = "-mobile" if mobile else ""
    target = config.output_dir / f"risk-calibration-and-beta{suffix}{style.suffix}.svg"
    save_svg(fig, target, style)
    config.qa_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        config.qa_dir / f"risk-calibration-and-beta{suffix}{style.suffix}.png",
        dpi=180,
        facecolor=style.background,
    )
    plt.close(fig)


def write_risk_figure_metadata(*, config: ArticleFigureConfig) -> None:
    """Persist the caption and source-to-asset manifest beside the evidence."""

    caption = (
        "Predicted versus realised risk (left) and 252-day realised market beta "
        "(right). Each calibration point pools all 1,444 offset-rebalance forecasts "
        "for one allocator and plots the square root of mean forecast/realised "
        "variance on "
        "both axes. Realised variance uses gross returns over the actual "
        "execution-to-next-execution holding window. All three books are evaluated "
        "with B2's covariance model; for B1 this is a common-model diagnostic, not "
        "a native constraint. B2 and B3 forecasts cluster near 7%, but realised "
        "risk remains higher. The grey beta band is the ±0.05 target range for "
        "B2/B3 target portfolios, not a guarantee for realised beta; each line is "
        "the mean of the three offset-specific rolling betas."
    )
    (config.review_dir / "risk_calibration_figure_caption.md").write_text(
        caption + "\n", encoding="utf-8"
    )
    manifest = {
        "display": "risk_calibration_and_realised_beta",
        "question": [
            "Does predicted risk match realised risk?",
            "Does realised market exposure stay controlled through time?",
        ],
        "evidence": [
            "outputs/review/risk_calibration_by_rebalance.csv",
            "outputs/review/risk_calibration_summary.csv",
            "outputs/review/risk_calibration_bins.csv",
            "outputs/review/risk_calibration_points.csv",
            "outputs/review/rolling_realised_beta_252d.csv",
        ],
        "article_assets": [
            "assets/portfolio-optimization/risk-calibration-and-beta.svg",
            "assets/portfolio-optimization/risk-calibration-and-beta_dark.svg",
            "assets/portfolio-optimization/risk-calibration-and-beta-mobile.svg",
            "assets/portfolio-optimization/risk-calibration-and-beta-mobile_dark.svg",
        ],
        "caption": caption,
        "visual_choices": {
            "calibration": (
                "one aggregate point per allocator; square root of mean variance "
                "on both axes with a 45-degree reference; bins remain audit-only"
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
    calibration, rolling_beta = build_risk_figure_data(config=config)
    for style in config.styles:
        for mobile in (False, True):
            plot_performance(data, style, config=config, mobile=mobile)
            plot_risk_calibration_and_beta(
                calibration,
                rolling_beta,
                style,
                config=config,
                mobile=mobile,
            )
    write_risk_figure_metadata(config=config)
    print(
        "Rendered eight SVGs from "
        f"{data.height:,} common-date observations ({data['date'].min()} to "
        f"{data['date'].max()}) and {calibration.height} calibration points."
    )


if __name__ == "__main__":
    main()
