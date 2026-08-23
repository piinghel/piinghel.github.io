"""Explicit data and rendering policy for regression article figures."""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class FigureStyle:
    benchmark: str = "#a7b1b8"
    ols: str = "#526777"
    ridge: str = "#756A8E"
    ink: str = "#33404b"
    muted: str = "#6a7883"
    grid: str = "#dbe1e3"
    white: str = "#ffffff"
    negative: str = "#756A8E"
    positive: str = "#6F91AD"
    long_leg: str = "#4F7396"
    short_leg: str = "#756A8E"
    net_exposure: str = "#56636D"
    tick_label_size: float = 9.2
    axis_label_size: float = 10.5
    legend_size: float = 9.5
    panel_title_size: float = 10.5
    annotation_size: float = 9.2
    output_suffix: str = ""


def dark_figure_style() -> FigureStyle:
    """Match the regression figures to the website's dark surface."""

    return FigureStyle(
        benchmark="#8B949E",
        ols="#91A4B5",
        ridge="#A093B8",
        ink="#C9D1D9",
        muted="#8B949E",
        grid="#30363D",
        white="#0D1117",
        negative="#A093B8",
        positive="#7FA4C4",
        long_leg="#78A0C4",
        short_leg="#A093B8",
        net_exposure="#AAB4BD",
        output_suffix="_dark",
    )


@dataclass(frozen=True)
class FigureSpec:
    model_order: tuple[str, ...]
    model_labels: Mapping[str, str]
    model_colors: Mapping[str, str]
    alpha_models: tuple[str, ...]
    split_date: date
    feature_labels: Mapping[str, str]


@dataclass(frozen=True)
class Series:
    dates: np.ndarray
    values: np.ndarray


def default_figure_spec(style: FigureStyle) -> FigureSpec:
    return FigureSpec(
        model_order=("fixed_factor_benchmark", "ols_c0", "selected_c0p01"),
        model_labels={
            "fixed_factor_benchmark": "Fixed weights",
            "ols_c0": "OLS",
            "selected_c0p01": "Ridge c = 0.01",
        },
        model_colors={
            "fixed_factor_benchmark": style.benchmark,
            "ols_c0": style.ols,
            "selected_c0p01": style.ridge,
        },
        alpha_models=(
            "alpha_0_ols",
            "alpha_scaled_c0p001",
            "alpha_scaled_c0p01_selected",
            "alpha_scaled_c0p1",
        ),
        split_date=date(2022, 1, 1),
        feature_labels={
            "X_feature_price_macd_10_21": "MACD · 10 / 21d",
            "X_feature_price_price_to_ma126": "Price / moving average · 126d",
            "X_feature_price_high_to_initial90_exclude10": "Prior high / start · 90d",
            "X_feature_pv_illiquidity_mean21": "Illiquidity · 21d mean",
            "X_feature_market_cap_log_std504": "Market-cap variability · 504d",
            "X_feature_liquidity_turnover_level63": "Share turnover · 63d",
            "X_feature_price_sharpe_ratio_compound_r126_volatility126_rolling": (
                "Historical Sharpe · 126d"
            ),
            "X_feature_market_cap_log_std21": "Market-cap variability · 21d",
            "X_feature_short_interest_to_volume_log_ratio": "Short interest / volume",
            "X_feature_price_price_to_min5": "Price / 5d low",
            "X_feature_price_rsi252": "RSI · 252d",
            "X_feature_price_atr126": "ATR · 126d",
            "X_feature_price_atr21": "ATR · 21d",
            "X_feature_price_upside_vol63": "Upside volatility · 63d",
            "X_feature_price_vol63": "Volatility · 63d",
            "X_feature_price_downside_vol252": "Downside volatility · 252d",
            "X_feature_price_downside_vol126": "Downside volatility · 126d",
            "X_feature_price_trend_streak200_126": "Trend streak · 200 / 126d",
            "X_feature_price_trend_streak200_252": "Trend streak · 200 / 252d",
            "X_feature_price_trend_streak200_504": "Trend streak · 200 / 504d",
            "X_feature_price_upside_vol252": "Upside volatility · 252d",
            "X_feature_price_final_to_high252_exclude21": ("Price / prior high · 252d"),
            "X_feature_price_macd_21_252": "MACD · 21 / 252d",
        },
    )


def read_rows(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else Path.open
    with opener(path, mode="rt", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError(f"no observations found in {path}")
    return rows


def load_daily_series(
    path: Path,
    *,
    value_column: str,
    model_order: tuple[str, ...],
) -> dict[str, Series]:
    grouped: dict[str, list[tuple[date, float]]] = defaultdict(list)
    for row in read_rows(path):
        grouped[row["model"]].append(
            (date.fromisoformat(row["date"]), float(row[value_column]))
        )
    missing = set(model_order) - set(grouped)
    if missing:
        raise ValueError(f"missing model series in {path.name}: {sorted(missing)}")
    series = {
        model: Series(
            np.array([item[0] for item in grouped[model]]),
            np.array([item[1] for item in grouped[model]]),
        )
        for model in model_order
    }
    date_vectors = [tuple(series[model].dates) for model in model_order]
    if any(vector != date_vectors[0] for vector in date_vectors[1:]):
        raise ValueError(f"model dates are not aligned in {path.name}")
    return series


def load_alpha_diagnostics(
    review_dir: Path,
    *,
    alpha_models: tuple[str, ...],
) -> dict[str, dict[str, str]]:
    diagnostics = {
        row["model"]: row
        for row in read_rows(review_dir / "multiple_linear_development_selection.csv")
        if row["model"] in alpha_models
    }
    for model in alpha_models:
        if model not in diagnostics:
            raise ValueError(f"missing development diagnostics for {model}")
    rank_changes = {
        row["model"]: row
        for row in read_rows(review_dir / "multiple_linear_rank_change_diagnostics.csv")
        if row["model"] in alpha_models and row["period"] == "development_1995_2021"
    }
    for model in alpha_models:
        if model not in rank_changes:
            raise ValueError(f"missing development rank-change diagnostics for {model}")
        diagnostics[model].update(rank_changes[model])
    return diagnostics


def load_selected_coefficients(review_dir: Path) -> list[dict[str, str]]:
    rows = read_rows(
        review_dir / "multiple_linear_selected_coefficient_heatmap_source_c0p01.csv.gz"
    )
    selected_by_key = {
        (row["feature"], row["fold_id"]): row
        for row in rows
        if int(row["heatmap_rank"]) <= 10
    }
    selected = list(selected_by_key.values())
    if len(selected) != 120:
        raise ValueError("expected ten selected predictors across twelve folds")
    if any(
        float(row["c"]) != 0.01 or row["selected"].lower() != "true" for row in selected
    ):
        raise ValueError("coefficient heatmap must use the selected c=0.01 model")
    return selected


def load_selected_portfolio_tilts(review_dir: Path) -> list[dict[str, str]]:
    rows = read_rows(
        review_dir
        / "multiple_linear_selected_portfolio_tilt_figure_source_c0p01.csv.gz"
    )
    if len(rows) != 1120 or len({row["predictor"] for row in rows}) != 10:
        raise ValueError("expected 112 quarters for ten selected portfolio tilts")
    if any(
        float(row["c"]) != 0.01 or row["selected"].lower() != "true" for row in rows
    ):
        raise ValueError("portfolio tilts must use the selected c=0.01 model")
    return rows


def load_selected_exposures(review_dir: Path) -> dict[str, Series]:
    """Load the retained monthly exposure paths for the selected portfolio."""

    rows = read_rows(review_dir / "multiple_linear_selected_exposure_figure_source.csv")
    dates = np.array([date.fromisoformat(row["date"]) for row in rows])
    return {
        column: Series(dates, np.array([float(row[column]) for row in rows]))
        for column in ("long_gross", "short_gross", "net_stock_exposure")
    }


def style_axis(
    ax: plt.Axes,
    style: FigureStyle,
    *,
    labelsize: float | None = None,
    grid_linewidth: float = 0.8,
) -> None:
    ax.grid(axis="y", color=style.grid, linewidth=grid_linewidth)
    ax.tick_params(
        axis="both",
        which="both",
        length=0,
        colors=style.muted,
        labelsize=style.tick_label_size if labelsize is None else labelsize,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_axisbelow(True)


def add_split_marker(
    ax: plt.Axes,
    style: FigureStyle,
    split_date: date,
    *,
    label: bool = False,
    label_fontsize: float = 8.0,
    label_text: str = "Specification fixed\nbefore 2022",
    label_at_top: bool = False,
) -> None:
    ax.axvline(split_date, color=style.muted, linewidth=0.9, linestyle=(0, (2, 3)))
    if label:
        ax.text(
            split_date + timedelta(days=-100 if label_at_top else 100),
            0.95 if label_at_top else 0.05,
            label_text,
            transform=ax.get_xaxis_transform(),
            color=style.muted,
            fontsize=label_fontsize,
            ha="right" if label_at_top else "left",
            va="top" if label_at_top else "bottom",
        )


def save_figure(
    fig: plt.Figure,
    output_dir: Path,
    stem: str,
    style: FigureStyle,
    *,
    mobile: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-mobile" if mobile else ""
    svg_path = output_dir / f"{stem}{suffix}{style.output_suffix}.svg"
    fig.savefig(
        svg_path,
        format="svg",
        facecolor=style.white,
        metadata={"Date": None},
    )
    lines = svg_path.read_text(encoding="utf-8").splitlines()
    svg_path.write_text(
        "\n".join(line.rstrip() for line in lines) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
