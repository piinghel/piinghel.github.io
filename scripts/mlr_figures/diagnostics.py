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
