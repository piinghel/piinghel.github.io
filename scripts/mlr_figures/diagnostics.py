"""Diagnostic figures for the multiple-linear-regression article."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch

from .support import (
    FigureSpec,
    FigureStyle,
    save_figure,
    style_axis,
)


def plot_factor_correlation(
    rows: list[dict[str, str]],
    output_dir: Path,
    style: FigureStyle,
) -> None:
    """Plot the distinct pairwise correlations among the five final factors."""

    factor_order = (
        "defensive",
        "momentum",
        "short_positioning",
        "size",
        "return_consistency",
    )
    factor_labels = {
        "defensive": "Defensive",
        "momentum": "Momentum",
        "short_positioning": "Short\npositioning",
        "size": "Size",
        "return_consistency": "Return\nconsistency",
    }
    lookup = {row["factor"]: row for row in rows}
    if len(rows) != len(factor_order) or set(lookup) != set(factor_order):
        raise ValueError("correlation matrix must contain the five final factors")
    matrix = np.array(
        [
            [float(lookup[row][column]) for column in factor_order]
            for row in factor_order
        ]
    )
    if (
        not np.isfinite(matrix).all()
        or not np.allclose(matrix, matrix.T)
        or not np.allclose(np.diag(matrix), 1)
    ):
        raise ValueError(
            "correlation matrix must be finite, symmetric, and unit diagonal"
        )

    values = np.full((4, 4), np.nan)
    for row_index, row_factor in enumerate(factor_order[1:]):
        for column_index, column_factor in enumerate(factor_order[:-1]):
            if column_index <= row_index:
                values[row_index, column_index] = float(
                    lookup[row_factor][column_factor]
                )

    color_map = LinearSegmentedColormap.from_list(
        "factor_correlation", (style.negative, style.white, style.positive)
    )
    color_map.set_bad(style.white)
    norm = TwoSlopeNorm(vmin=-0.3, vcenter=0.0, vmax=0.3)
    if np.nanmax(np.abs(values)) > 0.3:
        raise ValueError("factor correlations exceed the declared color scale")
    fig, ax = plt.subplots(figsize=(6.8, 4.7), facecolor=style.white)
    image = ax.pcolormesh(
        np.arange(5) - 0.5, np.arange(5) - 0.5, values, cmap=color_map, norm=norm
    )
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(3.5, -0.5)

    ax.set_xticks(
        np.arange(4),
        [factor_labels[factor] for factor in factor_order[:-1]],
    )
    ax.set_yticks(
        np.arange(4),
        [factor_labels[factor] for factor in factor_order[1:]],
    )
    ax.tick_params(
        axis="x",
        which="major",
        top=True,
        bottom=False,
        labeltop=True,
        labelbottom=False,
        length=0,
        pad=8,
        colors=style.ink,
        labelsize=style.tick_label_size,
        labelrotation=30,
    )
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("left")
        label.set_rotation_mode("anchor")
    ax.tick_params(
        axis="y",
        which="major",
        length=0,
        pad=8,
        colors=style.ink,
        labelsize=style.tick_label_size,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)

    for row_index in range(4):
        for column_index in range(row_index + 1):
            value = values[row_index, column_index]
            text_color = style.ink
            if abs(value) >= 0.22:
                text_color = "#0D1117" if style.output_suffix else "#FFFFFF"
            ax.text(
                column_index,
                row_index,
                f"{value:.2f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=style.annotation_size,
                fontweight=600,
            )

    colorbar = fig.colorbar(
        image,
        ax=ax,
        orientation="horizontal",
        fraction=0.07,
        pad=0.16,
        shrink=0.72,
        ticks=(-0.3, 0.0, 0.3),
    )
    colorbar.outline.set_visible(False)
    if colorbar.solids is not None:
        colorbar.solids.set_rasterized(False)
        colorbar.solids.set_edgecolor("face")
    colorbar.ax.tick_params(
        length=0,
        colors=style.muted,
        labelsize=style.tick_label_size,
    )
    fig.subplots_adjust(left=0.25, right=0.98, top=0.84, bottom=0.18)
    save_figure(fig, output_dir, "factor-correlation", style)


def plot_alpha_sensitivity(
    diagnostics: dict[str, dict[str, str]],
    output_dir: Path,
    style: FigureStyle,
    spec: FigureSpec,
) -> None:
    ridge_models = spec.alpha_models[1:]
    labels = ("c = 0.001", "c = 0.01", "c = 0.1")
    x = np.arange(len(ridge_models))
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8), facecolor=style.white)
    axes = np.asarray(axes).reshape(-1)
    for ax in axes:
        style_axis(ax, style)
        ax.set_xticks(x, labels)

    names_changed = [
        float(diagnostics[model]["mean_names_changed_of_150_vs_ols"])
        for model in ridge_models
    ]
    membership_bars = axes[0].bar(x, names_changed, width=0.72, color=style.ridge)
    axes[0].bar_label(
        membership_bars,
        labels=[f"{value:.1f}" for value in names_changed],
        padding=3,
        color=style.muted,
        fontsize=style.annotation_size,
    )
    axes[0].set_title(
        "A  Portfolio names changed vs OLS (of 150)",
        loc="left",
        color=style.ink,
        fontsize=style.panel_title_size,
        fontweight=600,
    )
    axes[0].set_ylim(0, 44)

    ols_l2 = float(diagnostics[spec.alpha_models[0]]["coefficient_l2_mean"])
    ols_change = float(
        diagnostics[spec.alpha_models[0]]["adjacent_fold_mean_abs_change_mean"]
    )
    l2_reduction = [
        100 * (1 - float(diagnostics[model]["coefficient_l2_mean"]) / ols_l2)
        for model in ridge_models
    ]
    movement_reduction = [
        100
        * (
            1
            - float(diagnostics[model]["adjacent_fold_mean_abs_change_mean"])
            / ols_change
        )
        for model in ridge_models
    ]
    width = 0.40
    norm_bars = axes[1].bar(
        x - width / 2,
        l2_reduction,
        width,
        color=style.ols,
        label="Coefficient norm",
    )
    movement_bars = axes[1].bar(
        x + width / 2,
        movement_reduction,
        width,
        color=style.ridge,
        label="Change between refits",
    )
    for bars, values in (
        (norm_bars, l2_reduction),
        (movement_bars, movement_reduction),
    ):
        axes[1].bar_label(
            bars,
            labels=[f"{value:.0f}%" for value in values],
            padding=3,
            color=style.muted,
            fontsize=style.annotation_size,
        )
    axes[1].set_ylim(0, 78)
    axes[1].set_title(
        "B  Coefficient shrinkage vs OLS (%)",
        loc="left",
        color=style.ink,
        fontsize=style.panel_title_size,
        fontweight=600,
    )
    axes[1].legend(
        frameon=False,
        fontsize=style.legend_size,
        labelcolor=style.ink,
        loc="upper left",
    )

    fig.subplots_adjust(
        left=0.07,
        right=0.98,
        top=0.89,
        bottom=0.19,
        hspace=0.0,
        wspace=0.25,
    )
    save_figure(fig, output_dir, "alpha-sensitivity", style)


def plot_turnover_costs(
    rows: list[dict[str, str]],
    output_dir: Path,
    style: FigureStyle,
) -> None:
    model_keys = (
        "fixed_factor_benchmark",
        "alpha_0_ols",
        "alpha_scaled_c0p01_selected",
    )
    labels = ("Fixed weights", "OLS", "Ridge c = 0.01")
    colors = (style.benchmark, style.ols, style.ridge)
    periods = ("development_1995_2021", "later_2022_2026")
    lookup = {(row["model"], row["period"]): row for row in rows}
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5), facecolor=style.white)
    axes = np.asarray(axes).reshape(-1)
    x = np.arange(len(model_keys))
    width = 0.34
    for ax, column, title in (
        (axes[0], "turnover_per_rebalance_pct", "Turnover per rebalance (%)"),
        (
            axes[1],
            "annual_cost_drag_pct_points",
            "Annual trading cost at 5 bp (pp)",
        ),
    ):
        style_axis(ax, style)
        for period_index, period in enumerate(periods):
            offset = (period_index - 0.5) * width
            values = [float(lookup[(model, period)][column]) for model in model_keys]
            bars = ax.bar(
                x + offset,
                values,
                width,
                color=colors,
                alpha=1.0 if period_index == 0 else 0.48,
            )
            if period_index == 1:
                for bar in bars:
                    bar.set_hatch("///")
                    bar.set_edgecolor(style.white)
        ax.set_title(
            title,
            loc="left",
            color=style.ink,
            fontsize=style.panel_title_size,
            fontweight=500,
        )
        ax.set_xticks(x, labels)
    legend_handles = (
        Patch(facecolor=style.muted, edgecolor="none", label="Development"),
        Patch(
            facecolor=style.muted,
            edgecolor=style.white,
            alpha=0.48,
            hatch="///",
            label="Later period",
        ),
    )
    fig.legend(
        handles=legend_handles,
        frameon=False,
        fontsize=style.legend_size,
        labelcolor=style.ink,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.54, 1.0),
    )
    fig.subplots_adjust(
        left=0.10,
        right=0.98,
        top=0.82,
        bottom=0.16,
        hspace=0.0,
        wspace=0.30,
    )
    save_figure(fig, output_dir, "turnover-and-costs", style)


def plot_selected_coefficients(
    rows: list[dict[str, str]],
    output_dir: Path,
    style: FigureStyle,
    spec: FigureSpec,
) -> None:
    features = [
        row["feature"]
        for row in sorted(rows, key=lambda item: int(item["heatmap_rank"]))
    ]
    features = list(dict.fromkeys(features))
    folds = sorted({int(row["fold_id"]) for row in rows})
    lookup = {
        (row["feature"], int(row["fold_id"])): float(row["coefficient"]) for row in rows
    }
    date_lookup = {
        int(row["fold_id"]): date.fromisoformat(row["test_date"]).year for row in rows
    }
    values = np.array(
        [[lookup[(feature, fold)] for fold in folds] for feature in features]
    )
    limit = float(np.max(np.abs(values)))
    color_map = LinearSegmentedColormap.from_list(
        "coefficient", (style.negative, style.white, style.positive)
    )
    fig, ax = plt.subplots(figsize=(9.6, 4.8), facecolor=style.white)
    ax.pcolormesh(
        np.arange(values.shape[1] + 1) - 0.5,
        np.arange(values.shape[0] + 1) - 0.5,
        values,
        cmap=color_map,
        norm=TwoSlopeNorm(vmin=-limit, vcenter=0.0, vmax=limit),
        shading="flat",
    )
    ax.set_xlim(-0.5, values.shape[1] - 0.5)
    ax.set_ylim(values.shape[0] - 0.5, -0.5)
    ax.set_xticks(
        np.arange(len(folds)),
        [str(date_lookup[fold]) for fold in folds],
        rotation=0,
        ha="center",
    )
    ax.set_yticks(
        np.arange(len(features)),
        [
            spec.feature_labels.get(feature, feature.removeprefix("X_feature_"))
            for feature in features
        ],
    )
    ax.tick_params(axis="x", which="both", length=0, colors=style.muted, labelsize=8.3)
    ax.tick_params(axis="y", which="both", length=0, colors=style.ink, labelsize=8.5)
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                f"{value:+.3f}",
                ha="center",
                va="center",
                color=style.white if abs(value) > 0.57 * limit else style.ink,
                fontsize=7.8,
            )
    ax.set_xticks(np.arange(-0.5, len(folds), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(features), 1), minor=True)
    ax.grid(which="minor", color=style.white, linewidth=1.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(
        left=0.29,
        right=0.99,
        top=0.98,
        bottom=0.14,
    )
    save_figure(fig, output_dir, "top-coefficients", style)


def plot_selected_portfolio_tilts(
    rows: list[dict[str, str]],
    output_dir: Path,
    style: FigureStyle,
    spec: FigureSpec,
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
    negative = sorted(
        (
            predictor
            for predictor in grouped
            if metadata[predictor]["side"] == "negative"
        ),
        key=lambda predictor: metadata[predictor]["side_rank"],
    )
    positive = sorted(
        (
            predictor
            for predictor in grouped
            if metadata[predictor]["side"] == "positive"
        ),
        key=lambda predictor: metadata[predictor]["side_rank"],
    )
    ordered = [item for pair in zip(negative, positive, strict=True) for item in pair]
    fig, axes = plt.subplots(5, 2, figsize=(9.6, 7.2), facecolor=style.white)
    axes = np.asarray(axes).reshape(-1)
    all_dates = [
        date.fromisoformat(row["date"])
        for predictor_rows in grouped.values()
        for row in predictor_rows
    ]
    first_date, last_date = min(all_dates), max(all_dates)
    visual_scale = 0.9
    for index, (ax, predictor) in enumerate(zip(axes, ordered, strict=True)):
        values = sorted(grouped[predictor], key=lambda row: row["date"])
        dates = np.array([date.fromisoformat(row["date"]) for row in values])
        tilts = np.array([float(row["quarterly_mean_tilt"]) for row in values])
        mean = float(metadata[predictor]["mean"])
        color = style.ridge if mean >= 0 else style.ols
        ax.plot(dates, tilts, color=color, linewidth=1.35 * visual_scale)
        ax.fill_between(dates, 0, tilts, color=color, alpha=0.10)
        ax.axhline(0, color=style.grid, linewidth=0.8 * visual_scale)
        lower = min(0.0, np.floor(float(np.min(tilts)) * 10) / 10)
        upper = max(0.0, np.ceil(float(np.max(tilts)) * 10) / 10)
        ax.set_ylim(lower, upper)
        ticks = [lower, upper]
        span = upper - lower
        if lower < 0 < upper and min(abs(lower), abs(upper)) / span >= 0.2:
            ticks.insert(1, 0.0)
        ticks = list(dict.fromkeys(ticks))
        ax.set_yticks(
            ticks,
            [
                "0" if value == 0 else f"{value:+.1f}".replace("-", "−")
                for value in ticks
            ],
        )
        ax.set_xlim(first_date, last_date)
        ax.margins(x=0)
        style_axis(
            ax,
            style,
            labelsize=style.tick_label_size * visual_scale,
            grid_linewidth=0.8 * visual_scale,
        )
        ax.set_title(
            spec.feature_labels.get(
                predictor,
                predictor.removeprefix("X_feature_"),
            ),
            loc="left",
            color=style.ink,
            fontsize=style.legend_size * visual_scale,
            fontweight=500,
            pad=4 * visual_scale,
        )
        ax.text(
            1.0,
            1.03,
            f"mean {mean:+.2f}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            color=color,
            fontsize=style.annotation_size * visual_scale,
            fontweight=600,
        )
        ax.xaxis.set_major_locator(mdates.YearLocator(8))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        show_x = index >= len(ordered) - 2
        if not show_x:
            ax.tick_params(axis="x", labelbottom=False)
    fig.subplots_adjust(
        left=0.10,
        right=0.98,
        top=0.97,
        bottom=0.06,
        hspace=0.56,
        wspace=0.25,
    )
    save_figure(fig, output_dir, "portfolio-feature-tilts", style)
