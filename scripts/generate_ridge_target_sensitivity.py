"""Generate the Ridge target-sensitivity figure used by the article."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "ridge"
DATA_PATH = (
    Path(__file__).resolve().parents[1] / "_data" / "ridge_target_sensitivity.csv"
)

COLORS = ["#477c80", "#6e999c", "#a8c2c3", "#667581", "#8b979f", "#bac1c6"]
INK = "#33404b"
MUTED = "#66737e"
GRID = "#dfe5e8"


def load_results(path: Path = DATA_PATH) -> tuple[list[str], dict[str, np.ndarray]]:
    """Load the compact evidence retained with the article."""
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 6:
        raise ValueError(
            f"expected six target specifications in {path}, found {len(rows)}"
        )
    labels = [row["label"] for row in rows]
    metrics = {
        "IC information ratio": np.array([float(row["ic_ir"]) for row in rows]),
        "Net portfolio Sharpe": np.array([float(row["net_sharpe"]) for row in rows]),
    }
    return labels, metrics


def clean_svg(path: Path) -> None:
    """Keep generated SVGs free of Matplotlib's trailing path whitespace."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def style_axis(
    ax: plt.Axes,
    title: str,
    values: np.ndarray,
    labels: list[str],
    show_labels: bool,
) -> None:
    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=COLORS, height=0.58, edgecolor="none")
    ax.invert_yaxis()
    ax.set_title(title, loc="left", color=INK, fontsize=11, fontweight=600, pad=10)
    ax.set_yticks(y)
    ax.set_yticklabels(labels if show_labels else [], color=MUTED, fontsize=8.7)
    ax.tick_params(axis="both", which="both", length=0, labelcolor=MUTED, labelsize=8)
    ax.xaxis.grid(True, color=GRID, linewidth=0.75, linestyle=(0, (1.5, 3)))
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    maximum = float(values.max())
    ax.set_xlim(0, maximum * 1.22)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_width() + maximum * 0.025,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}",
            va="center",
            ha="left",
            color=MUTED,
            fontsize=8.2,
            fontweight=500,
        )


def save_desktop() -> None:
    labels, metrics = load_results()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.25), facecolor="white")
    for index, (title, values) in enumerate(metrics.items()):
        style_axis(axes[index], title, values, labels, show_labels=index == 0)
    fig.subplots_adjust(left=0.245, right=0.985, top=0.86, bottom=0.12, wspace=0.34)
    svg_path = OUTPUT_DIR / "target-sensitivity.svg"
    fig.savefig(svg_path, format="svg", facecolor="white")
    clean_svg(svg_path)
    fig.savefig(OUTPUT_DIR / "target-sensitivity.png", dpi=500, facecolor="white")
    plt.close(fig)


def save_mobile() -> None:
    labels, metrics = load_results()
    fig, axes = plt.subplots(2, 1, figsize=(4.5, 5.4), facecolor="white")
    for axis, (title, values) in zip(axes, metrics.items(), strict=True):
        style_axis(axis, title, values, labels, show_labels=True)
    fig.subplots_adjust(left=0.43, right=0.95, top=0.94, bottom=0.08, hspace=0.34)
    svg_path = OUTPUT_DIR / "target-sensitivity-mobile.svg"
    fig.savefig(svg_path, format="svg", facecolor="white")
    clean_svg(svg_path)
    fig.savefig(
        OUTPUT_DIR / "target-sensitivity-mobile.png", dpi=500, facecolor="white"
    )
    plt.close(fig)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": "white",
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
        }
    )
    save_desktop()
    save_mobile()
