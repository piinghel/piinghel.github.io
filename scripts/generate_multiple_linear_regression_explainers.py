"""Generate the benchmark, normalization, and walk-forward article explainers."""

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "multiple-linear-regression"
COMPONENTS_PATH = ROOT / "_data" / "multiple_linear_regression_benchmark_components.csv"
SIGNAL_CORRELATIONS_PATH = (
    ROOT / "_data" / "multiple_linear_regression_benchmark_signal_correlations.csv"
)
RETURN_CORRELATIONS_PATH = (
    ROOT / "_data" / "multiple_linear_regression_benchmark_return_correlations.csv"
)

TEAL = "#477c80"
TEAL_LIGHT = "#dce9e9"
RED = "#a96760"
REFERENCE = "#76848e"
INK = "#33404b"
MUTED = "#66737e"
GRID = "#dfe5e8"
PANEL = "#f6f8f8"
WHITE = "#ffffff"


@dataclass(frozen=True)
class ComponentEvidence:
    key: str
    label: str
    short_label: str
    net_return_pct: float
    net_sharpe: float


def load_component_evidence(
    components_path: Path = COMPONENTS_PATH,
    signal_correlations_path: Path = SIGNAL_CORRELATIONS_PATH,
    return_correlations_path: Path = RETURN_CORRELATIONS_PATH,
) -> tuple[list[ComponentEvidence], np.ndarray, np.ndarray]:
    """Load and validate the retained standalone and correlation evidence."""
    with components_path.open(encoding="utf-8", newline="") as file:
        components = [
            ComponentEvidence(
                key=row["key"],
                label=row["label"],
                short_label=row["short_label"],
                net_return_pct=float(row["net_return_pct"]),
                net_sharpe=float(row["net_sharpe"]),
            )
            for row in csv.DictReader(file)
        ]
    if not components or any(
        component.net_return_pct <= 0 or component.net_sharpe <= 0
        for component in components
    ):
        raise ValueError(
            "every retained benchmark component must have positive net performance"
        )

    keys = [component.key for component in components]
    signal_matrix = load_correlation_matrix(signal_correlations_path, keys)
    return_matrix = load_correlation_matrix(return_correlations_path, keys)
    return components, signal_matrix, return_matrix


def load_correlation_matrix(path: Path, keys: list[str]) -> np.ndarray:
    """Load one ordered, symmetric component-correlation matrix."""
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if [row["key"] for row in rows] != keys:
        raise ValueError(f"correlation rows in {path.name} must match component order")
    matrix = np.array([[float(row[key]) for key in keys] for row in rows])
    if matrix.shape != (len(keys), len(keys)):
        raise ValueError("correlation matrix must be square")
    if not np.allclose(matrix, matrix.T) or not np.allclose(np.diag(matrix), 1.0):
        raise ValueError("correlation matrix must be symmetric with a unit diagonal")
    return matrix


def clean_svg(path: Path) -> None:
    """Remove trailing path whitespace from generated SVG files."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def save_figure(fig: plt.Figure, stem: str, mobile: bool = False) -> None:
    suffix = "-mobile" if mobile else ""
    svg_path = OUTPUT_DIR / f"{stem}{suffix}.svg"
    fig.savefig(svg_path, format="svg", facecolor=WHITE)
    clean_svg(svg_path)
    fig.savefig(OUTPUT_DIR / f"{stem}{suffix}.png", dpi=500, facecolor=WHITE)
    plt.close(fig)


def style_bar_axis(ax: plt.Axes, components: list[ComponentEvidence]) -> None:
    values = np.array([component.net_return_pct for component in components])
    y = np.arange(len(components))
    bars = ax.barh(y, values, color=TEAL, height=0.56, edgecolor="none")
    ax.invert_yaxis()
    ax.set_yticks(y)
    ax.set_yticklabels([component.label for component in components], color=MUTED)
    ax.set_xlim(0, 7.2)
    ax.set_title(
        "Standalone annualized arithmetic net return after costs",
        loc="left",
        color=INK,
        fontsize=11,
        fontweight=600,
        pad=10,
    )
    ax.xaxis.grid(True, color=GRID, linewidth=0.75, linestyle=(0, (1.5, 3)))
    ax.tick_params(axis="both", which="both", length=0, labelcolor=MUTED, labelsize=8.4)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            value + 0.12,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}%",
            ha="left",
            va="center",
            color=MUTED,
            fontsize=8.3,
            fontweight=500,
        )


def style_correlation_axis(
    ax: plt.Axes,
    components: list[ComponentEvidence],
    matrix: np.ndarray,
    *,
    short_labels: bool,
    title: str,
) -> None:
    labels = [
        component.short_label if short_labels else component.label
        for component in components
    ]
    display = matrix.copy()
    np.fill_diagonal(display, np.nan)
    cmap = LinearSegmentedColormap.from_list("factor_corr", [RED, WHITE, TEAL])
    cmap.set_bad(PANEL)
    boundaries = np.arange(len(labels) + 1) - 0.5
    ax.pcolormesh(
        boundaries,
        boundaries,
        display,
        cmap=cmap,
        norm=TwoSlopeNorm(vmin=-0.25, vcenter=0.0, vmax=0.90),
        shading="flat",
    )
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylim(len(labels) - 0.5, -0.5)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=38, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(labels)
    ax.tick_params(axis="both", which="both", length=0, labelcolor=MUTED, labelsize=7.5)
    ax.set_title(
        title,
        loc="left",
        color=INK,
        fontsize=11,
        fontweight=600,
        pad=10,
    )
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            label = "—" if row == column else f"{matrix[row, column]:.2f}"
            value = matrix[row, column]
            color = WHITE if row != column and (value > 0.58 or value < -0.16) else INK
            ax.text(
                column,
                row,
                label,
                ha="center",
                va="center",
                color=color,
                fontsize=7.2,
                fontweight=500,
            )
    for spine in ax.spines.values():
        spine.set_visible(False)


def save_benchmark_evidence() -> None:
    components, signal_matrix, return_matrix = load_component_evidence()

    fig, axes = plt.subplot_mosaic(
        [["performance", "performance"], ["signal", "return"]],
        figsize=(10.8, 8.0),
        facecolor=WHITE,
        height_ratios=[0.62, 1.0],
    )
    style_bar_axis(axes["performance"], components)
    style_correlation_axis(
        axes["signal"],
        components,
        signal_matrix,
        short_labels=True,
        title="Same-date signal rank correlation",
    )
    style_correlation_axis(
        axes["return"],
        components,
        return_matrix,
        short_labels=True,
        title="Realized net-return correlation",
    )
    fig.subplots_adjust(
        left=0.2,
        right=0.98,
        top=0.95,
        bottom=0.12,
        hspace=0.45,
        wspace=0.42,
    )
    save_figure(fig, "benchmark-component-evidence")

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(4.5, 11.3),
        facecolor=WHITE,
        gridspec_kw={"height_ratios": [0.72, 1.0, 1.0]},
    )
    style_bar_axis(axes[0], components)
    style_correlation_axis(
        axes[1],
        components,
        signal_matrix,
        short_labels=True,
        title="Same-date signal rank correlation",
    )
    style_correlation_axis(
        axes[2],
        components,
        return_matrix,
        short_labels=True,
        title="Realized net-return correlation",
    )
    fig.subplots_adjust(left=0.34, right=0.95, top=0.97, bottom=0.07, hspace=0.62)
    save_figure(fig, "benchmark-component-evidence", mobile=True)


def add_box(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    accent: bool = False,
) -> None:
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.06",
        linewidth=1.0,
        edgecolor=TEAL if accent else GRID,
        facecolor=TEAL_LIGHT if accent else PANEL,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        color=INK,
        fontsize=8.4,
        linespacing=1.25,
    )


def add_arrow(
    ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]
) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={"arrowstyle": "->", "color": REFERENCE, "lw": 1.0},
    )


def save_normalization_flow() -> None:
    rows = [
        (
            "Predictors",
            [
                "Raw predictor\nvalues",
                "Fill missing\nobservations",
                "Rank each predictor\nacross stocks that date",
                "Scale to\n[−1, 1]",
            ],
        ),
        (
            "Target",
            [
                "Forward\n20-session Sharpe",
                "Group by\ndate and sector",
                "Rank forward Sharpe\nwithin each sector",
                "Scale to\n[−1, 1]",
            ],
        ),
    ]
    fig, ax = plt.subplots(figsize=(10.6, 2.8), facecolor=WHITE)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 2.8)
    ax.axis("off")
    x_positions = [1.35, 3.75, 6.15, 8.55]
    for row_index, (label, boxes) in enumerate(rows):
        y = 1.65 - row_index * 1.15
        ax.text(
            0.05,
            y + 0.35,
            label,
            ha="left",
            va="center",
            color=INK,
            fontsize=10,
            fontweight=600,
        )
        for index, (x, text_value) in enumerate(zip(x_positions, boxes, strict=True)):
            add_box(ax, x, y, 1.75, 0.7, text_value, accent=index == len(boxes) - 1)
            if index:
                add_arrow(
                    ax, (x_positions[index - 1] + 1.78, y + 0.35), (x - 0.05, y + 0.35)
                )
    fig.subplots_adjust(left=0.02, right=0.99, top=0.98, bottom=0.02)
    save_figure(fig, "normalization-flow")

    fig, axes = plt.subplots(1, 2, figsize=(4.5, 5.9), facecolor=WHITE)
    for ax, (label, boxes) in zip(axes, rows, strict=True):
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 5.6)
        ax.axis("off")
        ax.text(
            1.0,
            5.38,
            label,
            ha="center",
            va="center",
            color=INK,
            fontsize=10,
            fontweight=600,
        )
        for index, text_value in enumerate(boxes):
            y = 4.35 - index * 1.25
            add_box(ax, 0.12, y, 1.76, 0.78, text_value, accent=index == len(boxes) - 1)
            if index:
                add_arrow(ax, (1.0, y + 1.02), (1.0, y + 0.82))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.02, wspace=0.12)
    save_figure(fig, "normalization-flow", mobile=True)


def save_walk_forward_flow() -> None:
    boxes = [
        "Past observations\nonly",
        "Leave out the\ntarget horizon",
        "Predict the next\nunseen block",
    ]
    fig, ax = plt.subplots(figsize=(9.6, 2.0), facecolor=WHITE)
    ax.set_xlim(0, 9.6)
    ax.set_ylim(0, 2.0)
    ax.axis("off")
    x_positions = [0.45, 3.65, 6.85]
    for index, (x, text_value) in enumerate(zip(x_positions, boxes, strict=True)):
        add_box(ax, x, 0.72, 2.25, 0.72, text_value, accent=index == len(boxes) - 1)
        if index:
            add_arrow(ax, (x_positions[index - 1] + 2.3, 1.08), (x - 0.05, 1.08))
    ax.text(
        4.8,
        0.28,
        "Expand the history, refit, and repeat →",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    save_figure(fig, "walk-forward")

    fig, ax = plt.subplots(figsize=(4.0, 4.6), facecolor=WHITE)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    for index, text_value in enumerate(boxes):
        y = 3.45 - index * 1.25
        add_box(ax, 0.8, y, 2.4, 0.78, text_value, accent=index == len(boxes) - 1)
        if index:
            add_arrow(ax, (2.0, y + 1.02), (2.0, y + 0.82))
    ax.text(
        2.0,
        0.32,
        "Expand, refit, repeat",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    save_figure(fig, "walk-forward", mobile=True)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": WHITE,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "svg.fonttype": "path",
        }
    )
    save_benchmark_evidence()
    save_normalization_flow()
    save_walk_forward_flow()
