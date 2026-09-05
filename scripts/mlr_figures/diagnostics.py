"""Diagnostic figures for the multiple-linear-regression article."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from .support import (
    FigureSpec,
    FigureStyle,
    save_figure,
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

    pairs = sorted(
        [
            (float(matrix[i, j]), factor_order[i], factor_order[j])
            for i in range(5)
            for j in range(i + 1, 5)
        ],
        reverse=True,
    )
    if any(abs(value) > 1 for value, _, _ in pairs):
        raise ValueError("correlations must lie within [-1, 1]")
    fig, ax = plt.subplots(figsize=(8.6, 4.6), facecolor=style.white)
    labels = [
        f"{factor_labels[left]} / {factor_labels[right]}".replace("\n", " ")
        for _, left, right in pairs
    ]
    values = np.array([value for value, _, _ in pairs])
    positions = np.arange(len(pairs))
    colors = [style.positive if value >= 0 else style.negative for value in values]
    ax.hlines(positions, 0, values, colors=style.grid, linewidth=1.5)
    ax.scatter(values, positions, c=colors, s=40, zorder=3)
    ax.axvline(0, color=style.muted, linewidth=0.7)
    ax.set_yticks(positions, labels, fontsize=11, color=style.ink)
    ax.set_ylim(len(pairs) - 0.5, -0.5)
    ax.set_xlim(
        min(-0.1, float(values.min()) - 0.04), max(0.35, float(values.max()) + 0.06)
    )
    ax.set_xlabel(
        "Mean Spearman rank correlation", fontsize=11, color=style.ink, labelpad=12
    )
    ax.tick_params(axis="x", labelsize=10.5, colors=style.muted, length=0)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.xaxis.grid(True, color=style.grid, linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for y, value in enumerate(values):
        ax.annotate(
            f"{value:.2f}",
            (value, y),
            xytext=(8, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=10.5,
            color=style.ink,
        )
    fig.subplots_adjust(left=0.43, right=0.97, top=0.98, bottom=0.16)
    save_figure(fig, output_dir, "factor-correlation", style)


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
    limit = float(np.max(np.abs(values))) or 1.0
    color_map = LinearSegmentedColormap.from_list(
        "coefficient", (style.negative, style.white, style.positive)
    )
    fig, ax = plt.subplots(figsize=(9.6, 5.6), facecolor=style.white)
    mesh = ax.pcolormesh(
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
    ax.set_xlabel("Refit year", color=style.ink, fontsize=10.5, labelpad=9)
    ax.tick_params(axis="x", which="both", length=0, colors=style.muted, labelsize=10)
    ax.tick_params(axis="y", which="both", length=0, colors=style.ink, labelsize=10)
    ax.set_xticks(np.arange(-0.5, len(folds), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(features), 1), minor=True)
    ax.grid(which="minor", color=style.white, linewidth=1.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(
        left=0.36,
        right=0.90,
        top=0.98,
        bottom=0.14,
    )
    color_axis = fig.add_axes((0.925, 0.25, 0.014, 0.62))
    colorbar = fig.colorbar(mesh, cax=color_axis)
    colorbar.solids.set_rasterized(False)
    colorbar.set_label("Coefficient", color=style.ink, fontsize=10)
    colorbar.ax.tick_params(colors=style.muted, labelsize=9, length=0)
    colorbar.outline.set_visible(False)
    save_figure(fig, output_dir, "top-coefficients", style)
