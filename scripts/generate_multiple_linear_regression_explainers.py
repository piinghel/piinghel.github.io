"""Generate the two benchmark-dependence panels used in the article."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "multiple-linear-regression"
SIGNAL_PATH = ROOT / "_data" / "multiple_linear_regression_benchmark_signal_correlations.csv"
RETURN_PATH = ROOT / "_data" / "multiple_linear_regression_benchmark_return_correlations.csv"

KEYS = (
    "low_vol",
    "upper_tail_avoidance",
    "momentum_3_6_9_12",
    "short_interest",
    "large_cap",
    "loss_frequency_756",
)
LABELS = (
    "Low vol",
    "Tail avoidance",
    "Momentum",
    "Short interest",
    "Large cap",
    "Return consistency",
)
INK = "#33404b"
MUTED = "#66737e"
PANEL = "#f6f8f8"
WHITE = "#ffffff"
TEAL = "#477c80"
CORAL = "#a96760"


def load_matrix(path: Path) -> np.ndarray:
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if [row["key"] for row in rows] != list(KEYS):
        raise ValueError(f"unexpected component order in {path.name}")
    matrix = np.array([[float(row[key]) for key in KEYS] for row in rows])
    if not np.allclose(matrix, matrix.T) or not np.allclose(np.diag(matrix), 1.0):
        raise ValueError(f"invalid correlation matrix in {path.name}")
    return matrix


def draw_heatmap(ax: plt.Axes, matrix: np.ndarray, title: str) -> None:
    display = matrix.copy()
    np.fill_diagonal(display, np.nan)
    cmap = LinearSegmentedColormap.from_list("factor_corr", (CORAL, WHITE, TEAL))
    cmap.set_bad(PANEL)
    bounds = np.arange(len(KEYS) + 1) - 0.5
    ax.pcolormesh(
        bounds,
        bounds,
        display,
        cmap=cmap,
        norm=TwoSlopeNorm(vmin=-0.25, vcenter=0, vmax=0.90),
        shading="flat",
    )
    ax.set_xlim(-0.5, len(KEYS) - 0.5)
    ax.set_ylim(len(KEYS) - 0.5, -0.5)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(len(KEYS)), LABELS, rotation=38, ha="right", rotation_mode="anchor")
    ax.set_yticks(np.arange(len(KEYS)), LABELS)
    ax.tick_params(axis="both", which="both", length=0, labelcolor=MUTED, labelsize=8.25)
    ax.set_title(title, loc="left", color=INK, fontsize=11.0, fontweight=600, pad=10)
    for row in range(len(KEYS)):
        for column in range(len(KEYS)):
            value = matrix[row, column]
            label = "—" if row == column else f"{value:.2f}"
            color = WHITE if row != column and (value > 0.58 or value < -0.16) else INK
            ax.text(column, row, label, ha="center", va="center", color=color, fontsize=8.0, fontweight=500)
    for spine in ax.spines.values():
        spine.set_visible(False)


def save(fig: plt.Figure, *, mobile: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "-mobile" if mobile else ""
    svg_path = OUTPUT_DIR / f"benchmark-dependence{suffix}.svg"
    fig.savefig(svg_path, format="svg", facecolor=WHITE)
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    fig.savefig(OUTPUT_DIR / f"benchmark-dependence{suffix}.png", dpi=240, facecolor=WHITE)
    plt.close(fig)


def main() -> None:
    signal = load_matrix(SIGNAL_PATH)
    returns = load_matrix(RETURN_PATH)
    for mobile in (False, True):
        if mobile:
            fig, axes = plt.subplots(2, 1, figsize=(4.6, 9.0), facecolor=WHITE)
            fig.subplots_adjust(left=0.35, right=0.97, top=0.98, bottom=0.08, hspace=0.58)
        else:
            fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.8), facecolor=WHITE)
            fig.subplots_adjust(left=0.17, right=0.98, top=0.94, bottom=0.20, wspace=0.42)
        draw_heatmap(axes[0], signal, "Same-date signal ranks")
        draw_heatmap(axes[1], returns, "Subsequent portfolio returns")
        save(fig, mobile=mobile)


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": WHITE, "savefig.bbox": "tight", "savefig.pad_inches": 0.04})
    main()
