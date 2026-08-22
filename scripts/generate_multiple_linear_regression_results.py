"""Generate matched OLS/Ridge article figures from retained compact evidence."""

from __future__ import annotations

import argparse
import csv
import gzip
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "assets" / "multiple-linear-regression"

BENCHMARK = "#a7b1b8"
OLS = "#526777"
RIDGE = "#3f8f88"
INK = "#33404b"
MUTED = "#6a7883"
GRID = "#dfe5e8"
WHITE = "#ffffff"
CORAL = "#d99a8b"
BLUE = "#6f9dbb"

MODEL_ORDER = ("fixed_factor_benchmark", "ols_c0", "selected_c0p01")
MODEL_LABEL = {
    "fixed_factor_benchmark": "Fixed weights",
    "ols_c0": "OLS",
    "selected_c0p01": "Ridge c = 0.01",
}
MODEL_COLOR = {
    "fixed_factor_benchmark": BENCHMARK,
    "ols_c0": OLS,
    "selected_c0p01": RIDGE,
}
ALPHA_MODELS = (
    "alpha_0_ols",
    "alpha_scaled_c0p001",
    "alpha_scaled_c0p01_selected",
    "alpha_scaled_c0p1",
)
ALPHA_LABELS = ("OLS\nc = 0", "Ridge\n0.001", "Ridge\n0.01", "Ridge\n0.1")
SPLIT_DATE = date(2022, 1, 1)

FEATURE_LABEL = {
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
    "X_feature_price_final_to_high252_exclude21": (
        "Price / prior high · 252d"
    ),
    "X_feature_price_macd_21_252": "MACD · 21 / 252d",
}


@dataclass(frozen=True)
class Series:
    dates: np.ndarray
    values: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--research-root",
        type=Path,
        required=True,
        help="Path to the factor_combination research project.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination for the article SVG and PNG files.",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else Path.open
    with opener(path, mode="rt", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError(f"no observations found in {path}")
    return rows


def load_daily_series(path: Path, *, value_column: str) -> dict[str, Series]:
    grouped: dict[str, list[tuple[date, float]]] = defaultdict(list)
    for row in read_rows(path):
        grouped[row["model"]].append(
            (date.fromisoformat(row["date"]), float(row[value_column]))
        )
    missing = set(MODEL_ORDER) - set(grouped)
    if missing:
        raise ValueError(f"missing model series in {path.name}: {sorted(missing)}")
    series = {
        model: Series(
            np.array([item[0] for item in grouped[model]]),
            np.array([item[1] for item in grouped[model]]),
        )
        for model in MODEL_ORDER
    }
    date_vectors = [tuple(series[model].dates) for model in MODEL_ORDER]
    if any(vector != date_vectors[0] for vector in date_vectors[1:]):
        raise ValueError(f"model dates are not aligned in {path.name}")
    return series


def load_alpha_diagnostics(
    review_dir: Path,
) -> dict[str, dict[str, str]]:
    diagnostics = {
        row["model"]: row
        for row in read_rows(
            review_dir / "multiple_linear_development_selection.csv"
        )
        if row["model"] in ALPHA_MODELS
    }
    for model in ALPHA_MODELS:
        if model not in diagnostics:
            raise ValueError(f"missing development diagnostics for {model}")
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
    if any(float(row["c"]) != 0.01 or row["selected"].lower() != "true" for row in selected):
        raise ValueError("coefficient heatmap must use the selected c=0.01 model")
    return selected


def load_selected_portfolio_tilts(review_dir: Path) -> list[dict[str, str]]:
    rows = read_rows(
        review_dir / "multiple_linear_selected_portfolio_tilt_figure_source_c0p01.csv.gz"
    )
    if len(rows) != 1120 or len({row["predictor"] for row in rows}) != 10:
        raise ValueError("expected 112 quarters for ten selected portfolio tilts")
    if any(float(row["c"]) != 0.01 or row["selected"].lower() != "true" for row in rows):
        raise ValueError("portfolio tilts must use the selected c=0.01 model")
    return rows


def style_axis(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=GRID, linewidth=0.75, linestyle=(0, (1.5, 3)))
    ax.tick_params(axis="both", which="both", length=0, colors=MUTED, labelsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.set_axisbelow(True)


def add_split_marker(ax: plt.Axes, *, label: bool = False) -> None:
    ax.axvline(SPLIT_DATE, color=MUTED, linewidth=0.9, linestyle=(0, (2, 3)))
    if label:
        ax.text(
            SPLIT_DATE + timedelta(days=100),
            0.05,
            "Specification fixed\nbefore 2022",
            transform=ax.get_xaxis_transform(),
            color=MUTED,
            fontsize=8,
            va="bottom",
        )


def clean_svg(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def save_figure(
    fig: plt.Figure, output_dir: Path, stem: str, *, mobile: bool = False
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-mobile" if mobile else ""
    svg_path = output_dir / f"{stem}{suffix}.svg"
    fig.savefig(svg_path, format="svg", facecolor=WHITE)
    clean_svg(svg_path)
    fig.savefig(output_dir / f"{stem}{suffix}.png", dpi=240, facecolor=WHITE)
    plt.close(fig)


def plot_ic(series: dict[str, Series], output_dir: Path, *, mobile: bool) -> None:
    size = (4.6, 5.1) if mobile else (10.2, 5.5)
    fig, ax = plt.subplots(figsize=size, facecolor=WHITE)
    for model in MODEL_ORDER:
        values = np.cumsum(series[model].values)
        ax.plot(
            series[model].dates,
            values,
            color=MODEL_COLOR[model],
            linewidth=2.0 if model == "selected_c0p01" else 1.6,
        )
        offset = {"fixed_factor_benchmark": -10, "ols_c0": 2, "selected_c0p01": 10}[
            model
        ]
        ax.annotate(
            MODEL_LABEL[model],
            (series[model].dates[-1], values[-1]),
            xytext=(7, offset),
            textcoords="offset points",
            color=MODEL_COLOR[model],
            fontsize=9,
            fontweight=600 if model == "selected_c0p01" else 400,
            va="center",
        )
    style_axis(ax)
    add_split_marker(ax, label=True)
    ax.set_ylabel("Cumulative daily rank IC", color=MUTED, fontsize=9.5)
    ax.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    right = series[MODEL_ORDER[0]].dates[-1] + timedelta(days=780 if mobile else 520)
    ax.set_xlim(series[MODEL_ORDER[0]].dates[0], right)
    fig.subplots_adjust(
        left=0.16 if mobile else 0.10,
        right=0.82 if mobile else 0.87,
        top=0.97,
        bottom=0.12,
    )
    save_figure(fig, output_dir, "cumulative-ic", mobile=mobile)


def plot_performance(
    wealth: dict[str, Series],
    drawdowns: dict[str, Series],
    output_dir: Path,
    *,
    mobile: bool,
) -> None:
    size = (4.6, 7.2) if mobile else (10.8, 6.7)
    fig, (wealth_ax, drawdown_ax) = plt.subplots(
        2,
        1,
        figsize=size,
        facecolor=WHITE,
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.08},
    )
    for axis in (wealth_ax, drawdown_ax):
        style_axis(axis)
        add_split_marker(axis, label=axis is drawdown_ax)
    for model in MODEL_ORDER:
        width = 2.0 if model == "selected_c0p01" else 1.5
        wealth_ax.plot(
            wealth[model].dates,
            wealth[model].values,
            color=MODEL_COLOR[model],
            linewidth=width,
        )
        drawdown_ax.plot(
            drawdowns[model].dates,
            drawdowns[model].values,
            color=MODEL_COLOR[model],
            linewidth=width - 0.2,
        )
        offset = {"fixed_factor_benchmark": -10, "ols_c0": 0, "selected_c0p01": 10}[
            model
        ]
        wealth_ax.annotate(
            MODEL_LABEL[model],
            (wealth[model].dates[-1], wealth[model].values[-1]),
            xytext=(7, offset),
            textcoords="offset points",
            color=MODEL_COLOR[model],
            fontsize=8.7,
            fontweight=600 if model == "selected_c0p01" else 400,
            va="center",
        )
    wealth_ax.axhline(1.0, color=MUTED, linewidth=0.7, linestyle=(0, (2, 3)))
    wealth_ax.set_yscale("log")
    wealth_ax.set_ylabel("Growth of $1", color=MUTED, fontsize=9.5)
    wealth_ax.yaxis.set_major_locator(FixedLocator([1, 2, 3, 4, 6, 8]))
    wealth_ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}×"))
    wealth_ax.yaxis.set_minor_formatter(NullFormatter())
    drawdown_ax.axhline(0, color=MUTED, linewidth=0.7, linestyle=(0, (2, 3)))
    drawdown_ax.set_ylabel("Drawdown (%)", color=MUTED, fontsize=9.5)
    drawdown_ax.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 4))
    drawdown_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    right = wealth[MODEL_ORDER[0]].dates[-1] + timedelta(days=780 if mobile else 520)
    drawdown_ax.set_xlim(wealth[MODEL_ORDER[0]].dates[0], right)
    fig.subplots_adjust(
        left=0.17 if mobile else 0.10,
        right=0.82 if mobile else 0.87,
        top=0.98,
        bottom=0.08,
    )
    save_figure(fig, output_dir, "performance-and-drawdowns", mobile=mobile)


def plot_alpha_sensitivity(
    diagnostics: dict[str, dict[str, str]],
    output_dir: Path,
    *,
    mobile: bool,
) -> None:
    x = np.arange(len(ALPHA_MODELS))
    size = (4.6, 10.0) if mobile else (10.6, 7.6)
    layout = (3, 1) if mobile else (1, 3)
    fig, axes = plt.subplots(*layout, figsize=size, facecolor=WHITE)
    axes = np.asarray(axes).reshape(-1)
    for ax in axes:
        style_axis(ax)
        ax.set_xticks(x, ALPHA_LABELS)

    for column, label, color, marker in (
        ("development_sharpe", "Full development", OLS, "o"),
        ("final_10y_sharpe", "Final 10 years", RIDGE, "s"),
        ("final_5y_sharpe", "Final 5 years", CORAL, "^"),
    ):
        values = [float(diagnostics[model][column]) for model in ALPHA_MODELS]
        axes[0].plot(
            x, values, color=color, marker=marker, linewidth=1.7, markersize=4.5
        )
        axes[0].text(
            x[-1] + (0.08 if mobile else -0.08),
            values[-1],
            label,
            color=color,
            fontsize=8,
            ha="left" if mobile else "right",
            va="center",
        )
    axes[0].set_title(
        "Sharpe across development windows",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight=600,
    )
    axes[0].set_ylabel("Net Sharpe ratio", color=MUTED, fontsize=9)
    axes[0].set_ylim(0.90, 1.16)

    prediction_corr = [
        100 * float(diagnostics[model]["prediction_rank_corr_ols"])
        for model in ALPHA_MODELS
    ]
    axes[1].plot(
        x, prediction_corr, color=RIDGE, marker="o", linewidth=1.8, markersize=4.5
    )
    axes[1].set_ylim(92, 100.7)
    axes[1].set_title(
        "Rank similarity to OLS",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight=600,
    )
    axes[1].set_ylabel(
        "Prediction rank correlation with OLS (%)", color=MUTED, fontsize=9
    )
    for position, value in zip(x, prediction_corr, strict=True):
        axes[1].text(
            position,
            value - 0.55,
            f"{value:.2f}",
            ha="center",
            va="top",
            color=MUTED,
            fontsize=7.8,
        )

    ols_l2 = float(diagnostics[ALPHA_MODELS[0]]["coefficient_l2_mean"])
    ols_change = float(
        diagnostics[ALPHA_MODELS[0]]["adjacent_fold_mean_abs_change_mean"]
    )
    l2 = [
        100 * float(diagnostics[model]["coefficient_l2_mean"]) / ols_l2
        for model in ALPHA_MODELS
    ]
    change = [
        100
        * float(diagnostics[model]["adjacent_fold_mean_abs_change_mean"])
        / ols_change
        for model in ALPHA_MODELS
    ]
    axes[2].plot(x, l2, color=OLS, marker="o", linewidth=1.7, markersize=4.5)
    axes[2].plot(x, change, color=RIDGE, marker="s", linewidth=1.7, markersize=4.5)
    axes[2].text(
        x[-1] + 0.08,
        l2[-1] + (3.0 if mobile else 0.0),
        "Coefficient L2",
        color=OLS,
        fontsize=8,
        va="center",
    )
    axes[2].text(
        x[-1] + 0.08,
        change[-1] - (3.0 if mobile else 0.0),
        "Change at refit",
        color=RIDGE,
        fontsize=8,
        va="center",
    )
    axes[2].set_ylim(0, 108)
    axes[2].set_title(
        "Coefficient size and movement",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight=600,
    )
    axes[2].set_ylabel("Relative to OLS (OLS = 100)", color=MUTED, fontsize=9)

    fig.subplots_adjust(
        left=0.18 if mobile else 0.08,
        right=0.83 if mobile else 0.94,
        top=0.97 if mobile else 0.92,
        bottom=0.07 if mobile else 0.16,
        hspace=0.62 if mobile else 0.0,
        wspace=0.40 if not mobile else 0.0,
    )
    save_figure(fig, output_dir, "alpha-sensitivity", mobile=mobile)


def plot_turnover_costs(
    rows: list[dict[str, str]], output_dir: Path, *, mobile: bool
) -> None:
    model_keys = ("fixed_factor_benchmark", "alpha_0_ols", "alpha_scaled_c0p01_selected")
    labels = ("Fixed weights", "OLS", "Ridge c = 0.01")
    colors = (BENCHMARK, OLS, RIDGE)
    periods = ("development_1995_2021", "later_2022_2026")
    period_labels = ("Development", "Later period")
    lookup = {(row["model"], row["period"]): row for row in rows}
    size = (4.6, 7.2) if mobile else (10.2, 4.5)
    layout = (2, 1) if mobile else (1, 2)
    fig, axes = plt.subplots(*layout, figsize=size, facecolor=WHITE)
    axes = np.asarray(axes).reshape(-1)
    x = np.arange(len(model_keys))
    width = 0.34
    for ax, column, title, ylabel in (
        (axes[0], "turnover_per_rebalance_pct", "Turnover", "Two-way turnover per rebalance (%)"),
        (axes[1], "annual_cost_drag_pct_points", "Costs at 5 bp", "Annual return drag (percentage points)"),
    ):
        style_axis(ax)
        for period_index, (period, period_label) in enumerate(zip(periods, period_labels, strict=True)):
            offset = (period_index - 0.5) * width
            values = [float(lookup[(model, period)][column]) for model in model_keys]
            bars = ax.bar(x + offset, values, width, color=colors, alpha=1.0 if period_index == 0 else 0.48)
            if period_index == 1:
                for bar in bars:
                    bar.set_hatch("///")
                    bar.set_edgecolor(WHITE)
            ax.plot([], [], color=MUTED, alpha=1.0 if period_index == 0 else 0.48,
                    linewidth=7, label=period_label)
        ax.set_title(title, loc="left", color=INK, fontsize=10.5, fontweight=600)
        ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
        ax.set_xticks(x, labels)
        ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    fig.subplots_adjust(
        left=0.20 if mobile else 0.09,
        right=0.98,
        top=0.96 if mobile else 0.91,
        bottom=0.09 if mobile else 0.16,
        hspace=0.48 if mobile else 0.0,
        wspace=0.30 if not mobile else 0.0,
    )
    save_figure(fig, output_dir, "turnover-and-costs", mobile=mobile)


def plot_selected_coefficients(
    rows: list[dict[str, str]], output_dir: Path, *, mobile: bool
) -> None:
    features = [
        row["feature"]
        for row in sorted(rows, key=lambda item: int(item["heatmap_rank"]))
    ]
    features = list(dict.fromkeys(features))
    folds = sorted({int(row["fold_id"]) for row in rows})
    if mobile:
        folds = [0, 2, 4, 7, 9, 11]
    lookup = {
        (row["feature"], int(row["fold_id"])): float(row["coefficient"])
        for row in rows
    }
    date_lookup = {
        int(row["fold_id"]): date.fromisoformat(row["test_date"]).year for row in rows
    }
    values = np.array(
        [[lookup[(feature, fold)] for fold in folds] for feature in features]
    )
    limit = float(np.max(np.abs(values)))
    color_map = LinearSegmentedColormap.from_list(
        "coefficient", (CORAL, "#f7f7f5", BLUE)
    )
    size = (4.6, 6.8) if mobile else (11.0, 5.4)
    fig, ax = plt.subplots(figsize=size, facecolor=WHITE)
    ax.imshow(
        values,
        cmap=color_map,
        norm=TwoSlopeNorm(vmin=-limit, vcenter=0.0, vmax=limit),
        aspect="auto",
    )
    ax.set_xticks(
        np.arange(len(folds)),
        [str(date_lookup[fold]) for fold in folds],
        rotation=45,
        ha="right",
    )
    ax.set_yticks(
        np.arange(len(features)),
        [FEATURE_LABEL.get(feature, feature.removeprefix("X_feature_")) for feature in features],
    )
    ax.tick_params(axis="x", which="both", length=0, colors=MUTED, labelsize=8.2)
    ax.tick_params(axis="y", which="both", length=0, colors=INK, labelsize=8.7)
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                f"{value:+.3f}",
                ha="center",
                va="center",
                color=WHITE if abs(value) > 0.57 * limit else INK,
                fontsize=7.3 if mobile else 7.8,
            )
    ax.set_xticks(np.arange(-0.5, len(folds), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(features), 1), minor=True)
    ax.grid(which="minor", color=WHITE, linewidth=1.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(
        "Blue raises the learned score · coral lowers it",
        loc="left",
        color=MUTED,
        fontsize=9,
        pad=10,
    )
    fig.subplots_adjust(
        left=0.43 if mobile else 0.29,
        right=0.99,
        top=0.94,
        bottom=0.10 if mobile else 0.14,
    )
    save_figure(fig, output_dir, "top-coefficients", mobile=mobile)


def plot_selected_portfolio_tilts(
    rows: list[dict[str, str]], output_dir: Path, *, mobile: bool
) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["predictor"]].append(row)
    metadata = {
        predictor: {
            "side": values[0]["side"],
            "side_rank": int(values[0]["side_rank"]),
            "tilt_rank": int(values[0]["tilt_rank"]),
            "mean": float(values[0]["mean"]),
        }
        for predictor, values in grouped.items()
    }
    if mobile:
        ordered = sorted(grouped, key=lambda predictor: metadata[predictor]["tilt_rank"])
        fig, axes = plt.subplots(10, 1, figsize=(4.6, 17.0), facecolor=WHITE)
    else:
        negative = sorted(
            (predictor for predictor in grouped if metadata[predictor]["side"] == "negative"),
            key=lambda predictor: metadata[predictor]["side_rank"],
        )
        positive = sorted(
            (predictor for predictor in grouped if metadata[predictor]["side"] == "positive"),
            key=lambda predictor: metadata[predictor]["side_rank"],
        )
        ordered = [item for pair in zip(negative, positive, strict=True) for item in pair]
        fig, axes = plt.subplots(5, 2, figsize=(11.0, 10.2), facecolor=WHITE)
    axes = np.asarray(axes).reshape(-1)
    for index, (ax, predictor) in enumerate(zip(axes, ordered, strict=True)):
        values = sorted(grouped[predictor], key=lambda row: row["date"])
        dates = np.array([date.fromisoformat(row["date"]) for row in values])
        tilts = np.array([float(row["quarterly_mean_tilt"]) for row in values])
        mean = metadata[predictor]["mean"]
        color = RIDGE if mean >= 0 else OLS
        ax.plot(dates, tilts, color=color, linewidth=1.35)
        ax.fill_between(dates, 0, tilts, color=color, alpha=0.10)
        ax.axhline(0, color=GRID, linewidth=0.8)
        ax.set_ylim(-0.92, 0.92)
        ax.set_yticks((-0.8, 0.0, 0.8), ("−0.8", "0", "+0.8"))
        style_axis(ax)
        ax.set_title(
            FEATURE_LABEL.get(predictor, predictor.removeprefix("X_feature_")),
            loc="left",
            color=INK,
            fontsize=9.3,
            fontweight=500,
            pad=4,
        )
        ax.text(
            1.0,
            1.03,
            f"mean {mean:+.2f}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            color=color,
            fontsize=8.4,
            fontweight=600,
        )
        ax.xaxis.set_major_locator(mdates.YearLocator(7 if mobile else 8))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        show_x = index == len(ordered) - 1 if mobile else index >= len(ordered) - 2
        if not show_x:
            ax.tick_params(axis="x", labelbottom=False)
    fig.supylabel(
        "Long − short predictor-rank tilt",
        color=MUTED,
        fontsize=10,
        x=0.025 if mobile else 0.035,
    )
    fig.subplots_adjust(
        left=0.18 if mobile else 0.10,
        right=0.98,
        top=0.99,
        bottom=0.045 if mobile else 0.06,
        hspace=0.62 if mobile else 0.55,
        wspace=0.25 if not mobile else 0.0,
    )
    save_figure(fig, output_dir, "portfolio-feature-tilts", mobile=mobile)


def main() -> None:
    args = parse_args()
    review_dir = args.research_root.resolve() / "outputs" / "review"
    output_dir = args.output_dir.resolve()
    ic = load_daily_series(
        review_dir / "multiple_linear_selected_daily_ic_figure_source.csv.gz",
        value_column="daily_rank_ic",
    )
    wealth = load_daily_series(
        review_dir / "multiple_linear_selected_return_drawdown_figure_source.csv.gz",
        value_column="cumulative_net_return_pct",
    )
    wealth = {
        model: Series(item.dates, 1.0 + item.values / 100.0)
        for model, item in wealth.items()
    }
    drawdowns = load_daily_series(
        review_dir / "multiple_linear_selected_return_drawdown_figure_source.csv.gz",
        value_column="drawdown_pct",
    )
    diagnostics = load_alpha_diagnostics(review_dir)
    period_metrics = read_rows(review_dir / "multiple_linear_period_portfolio_metrics.csv")
    selected_coefficients = load_selected_coefficients(review_dir)
    selected_portfolio_tilts = load_selected_portfolio_tilts(review_dir)

    for mobile in (False, True):
        plot_ic(ic, output_dir, mobile=mobile)
        plot_performance(wealth, drawdowns, output_dir, mobile=mobile)
        plot_alpha_sensitivity(
            diagnostics,
            output_dir,
            mobile=mobile,
        )
        plot_selected_coefficients(
            selected_coefficients,
            output_dir,
            mobile=mobile,
        )
        plot_selected_portfolio_tilts(
            selected_portfolio_tilts,
            output_dir,
            mobile=mobile,
        )
        plot_turnover_costs(period_metrics, output_dir, mobile=mobile)


if __name__ == "__main__":
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": WHITE,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
        }
    )
    main()
