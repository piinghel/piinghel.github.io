"""Generate the benchmark-dependence and walk-forward article figures."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle

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
X_LABELS = (
    "Low\nvol",
    "Tail\navoidance",
    "Momentum",
    "Short\ninterest",
    "Large\ncap",
    "Return\nconsistency",
)
INK = "#33404b"
MUTED = "#66737e"
PANEL = "#f6f8f8"
WHITE = "#ffffff"
TEAL = "#477c80"
CORAL = "#a96760"
TRAINING = "#417795"
GAP = "#ca7069"
TEST = "#409b93"

TICK_LABEL_SIZE = 9.2
PANEL_TITLE_SIZE = 10.5
CELL_LABEL_SIZE = 8.8


def load_matrix(path: Path) -> np.ndarray:
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if [row["key"] for row in rows] != list(KEYS):
        raise ValueError(f"unexpected component order in {path.name}")
    matrix = np.array([[float(row[key]) for key in KEYS] for row in rows])
    if not np.allclose(matrix, matrix.T) or not np.allclose(np.diag(matrix), 1.0):
        raise ValueError(f"invalid correlation matrix in {path.name}")
    return matrix


def draw_heatmap(
    ax: plt.Axes, matrix: np.ndarray, title: str, *, mobile: bool
) -> None:
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
    ax.set_xticks(np.arange(len(KEYS)), X_LABELS, rotation=0, ha="center")
    ax.set_yticks(np.arange(len(KEYS)), LABELS)
    ax.tick_params(
        axis="y",
        which="both",
        length=0,
        labelcolor=MUTED,
        labelsize=TICK_LABEL_SIZE,
    )
    ax.tick_params(
        axis="x",
        which="both",
        length=0,
        labelcolor=MUTED,
        labelsize=7.4 if mobile else TICK_LABEL_SIZE,
    )
    ax.set_title(
        title,
        loc="left",
        color=INK,
        fontsize=PANEL_TITLE_SIZE,
        fontweight=500,
        pad=10,
    )
    for row in range(len(KEYS)):
        for column in range(len(KEYS)):
            value = matrix[row, column]
            label = "—" if row == column else f"{value:.2f}"
            color = WHITE if row != column and (value > 0.58 or value < -0.16) else INK
            ax.text(
                column,
                row,
                label,
                ha="center",
                va="center",
                color=color,
                fontsize=CELL_LABEL_SIZE,
                fontweight=500,
            )
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_walk_forward(*, mobile: bool) -> plt.Figure:
    fig, ax = plt.subplots(
        figsize=(4.6, 5.0) if mobile else (10.0, 3.3),
        facecolor=WHITE,
    )
    ax.set_xlim(-0.16, 1.01)
    ax.set_ylim(0.45, 3.85)
    ax.axis("off")

    ax.text(
        0,
        3.75,
        "time →",
        color=MUTED,
        fontsize=12.0 if mobile else 11.0,
        fontweight=600,
        va="bottom",
    )
    ax.plot([0, 1], [3.62, 3.62], color="#dbe1e3", linewidth=1.0)

    height = 0.34
    rows = (
        ("Fit 1", 3.02, 0.35),
        ("Fit 2", 2.18, 0.61),
        ("Fit k", 0.82, 0.86),
    )
    for label, y, training_end in rows:
        ax.text(
            -0.15,
            y,
            label,
            color="#21334a",
            fontsize=11.0 if mobile else 10.5,
            fontweight=700,
            ha="left",
            va="center",
        )
        ax.add_patch(Rectangle((0, y - height / 2), 1, height, color="#eef1f3"))
        ax.add_patch(
            Rectangle((0, y - height / 2), training_end, height, color=TRAINING)
        )
        ax.add_patch(
            Rectangle(
                (training_end, y - height / 2),
                0.02,
                height,
                color=GAP,
            )
        )
        ax.add_patch(
            Rectangle(
                (training_end + 0.02, y - height / 2),
                min(0.23, 0.98 - training_end),
                height,
                color=TEST,
            )
        )

    ax.text(
        -0.15,
        1.50,
        "Fit …",
        color="#21334a",
        fontsize=11.0 if mobile else 10.5,
        fontweight=700,
        ha="left",
        va="center",
    )
    handles = (
        Patch(facecolor=TRAINING, edgecolor="none", label="training history (starts at 900 dates)"),
        Patch(facecolor=GAP, edgecolor="none", label="21-date gap"),
        Patch(facecolor=TEST, edgecolor="none", label="next 600-date test block"),
    )
    if mobile:
        fig.legend(
            handles=handles,
            frameon=False,
            fontsize=9.6,
            ncol=1,
            loc="lower left",
            bbox_to_anchor=(0.19, 0.01),
            labelcolor=MUTED,
            handlelength=1.0,
            handleheight=1.0,
            borderaxespad=0,
        )
        fig.subplots_adjust(left=0.18, right=0.98, top=0.98, bottom=0.34)
    else:
        fig.legend(
            handles=handles,
            frameon=False,
            fontsize=9.4,
            ncol=3,
            loc="lower center",
            bbox_to_anchor=(0.56, 0.02),
            labelcolor=MUTED,
            handlelength=0.9,
            columnspacing=2.2,
            borderaxespad=0,
        )
        fig.subplots_adjust(left=0.11, right=0.99, top=0.98, bottom=0.21)
    return fig


def save(fig: plt.Figure, stem: str, *, mobile: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "-mobile" if mobile else ""
    svg_path = OUTPUT_DIR / f"{stem}{suffix}.svg"
    fig.savefig(svg_path, format="svg", facecolor=WHITE)
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    fig.savefig(OUTPUT_DIR / f"{stem}{suffix}.png", dpi=240, facecolor=WHITE)
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
        draw_heatmap(axes[0], signal, "Same-date signal ranks", mobile=mobile)
        draw_heatmap(
            axes[1], returns, "Subsequent portfolio returns", mobile=mobile
        )
        save(fig, "benchmark-dependence", mobile=mobile)
        save(draw_walk_forward(mobile=mobile), "walk-forward", mobile=mobile)


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": WHITE, "savefig.bbox": "tight", "savefig.pad_inches": 0.04})
    main()
