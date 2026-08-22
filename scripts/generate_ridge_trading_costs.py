"""Generate the Ridge turnover and gross-to-net return comparison."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "ridge"
MODELS = ["Multifactor", "Ridge"]
TURNOVER = np.array([13.5, 28.7])
GROSS_RETURN = np.array([7.66, 8.53])
NET_RETURN = np.array([6.98, 7.09])

TEAL = "#477c80"
REFERENCE = "#76848e"
COST = "#d7b69d"
INK = "#33404b"
MUTED = "#66737e"
GRID = "#dfe5e8"


def clean_svg(path: Path) -> None:
    """Keep generated SVGs free of Matplotlib's trailing path whitespace."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def base_axis(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, loc="left", color=INK, fontsize=11, fontweight=600, pad=10)
    ax.tick_params(axis="both", which="both", length=0, labelcolor=MUTED, labelsize=8.5)
    ax.xaxis.grid(True, color=GRID, linewidth=0.75, linestyle=(0, (1.5, 3)))
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)


def turnover_panel(ax: plt.Axes, show_labels: bool = True) -> None:
    y = np.arange(len(MODELS))
    bars = ax.barh(y, TURNOVER, color=[REFERENCE, TEAL], height=0.46)
    ax.invert_yaxis()
    ax.set_yticks(y)
    ax.set_yticklabels(MODELS if show_labels else [], color=MUTED, fontsize=9)
    ax.set_xlim(0, 33)
    base_axis(ax, "Annualized two-way turnover")
    for bar, value in zip(bars, TURNOVER, strict=True):
        ax.text(
            value + 0.7,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}×",
            ha="left",
            va="center",
            color=MUTED,
            fontsize=9,
            fontweight=500,
        )


def return_panel(ax: plt.Axes, show_labels: bool = False) -> None:
    y = np.arange(len(MODELS))
    height = 0.46
    ax.barh(y, NET_RETURN, color=[REFERENCE, TEAL], height=height)
    ax.barh(y, GROSS_RETURN - NET_RETURN, left=NET_RETURN, color=COST, height=height)
    ax.invert_yaxis()
    ax.set_yticks(y)
    ax.set_yticklabels(MODELS if show_labels else [], color=MUTED, fontsize=9)
    ax.set_xlim(0, 10.7)
    base_axis(ax, "Annualized return")
    for row, (net, gross) in enumerate(zip(NET_RETURN, GROSS_RETURN, strict=True)):
        ax.text(net - 0.12, row, f"Net {net:.2f}%", ha="right", va="center", color="white", fontsize=8.5, fontweight=600)
        ax.text(gross + 0.14, row, f"Gross {gross:.2f}%", ha="left", va="center", color=MUTED, fontsize=8.5, fontweight=500)


def save_desktop() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 2.55), facecolor="white")
    turnover_panel(axes[0], show_labels=True)
    return_panel(axes[1], show_labels=False)
    fig.subplots_adjust(left=0.16, right=0.985, top=0.78, bottom=0.18, wspace=0.31)
    svg_path = OUTPUT_DIR / "turnover-and-costs.svg"
    fig.savefig(svg_path, format="svg", facecolor="white")
    clean_svg(svg_path)
    fig.savefig(OUTPUT_DIR / "turnover-and-costs.png", dpi=500, facecolor="white")
    plt.close(fig)


def save_mobile() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(4.5, 4.4), facecolor="white")
    turnover_panel(axes[0], show_labels=True)
    return_panel(axes[1], show_labels=True)
    fig.subplots_adjust(left=0.30, right=0.95, top=0.91, bottom=0.08, hspace=0.62)
    svg_path = OUTPUT_DIR / "turnover-and-costs-mobile.svg"
    fig.savefig(svg_path, format="svg", facecolor="white")
    clean_svg(svg_path)
    fig.savefig(OUTPUT_DIR / "turnover-and-costs-mobile.png", dpi=500, facecolor="white")
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
