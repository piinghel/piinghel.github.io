"""Generate the walk-forward article figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "multiple-linear-regression"
MUTED = "#66737e"
WHITE = "#ffffff"
TRAINING = "#4F7396"
GAP = "#756A8E"
TEST = "#7C8995"


def draw_walk_forward(*, mobile: bool) -> plt.Figure:
    fig, ax = plt.subplots(
        figsize=(4.6, 5.0) if mobile else (10.0, 3.3),
        facecolor=WHITE,
    )
    ax.set_xlim(-0.16, 1.01)
    ax.set_ylim(0.20 if mobile else 0.45, 3.85)
    ax.axis("off")

    time_arrow = FancyArrowPatch(
        (0, 3.62),
        (1, 3.62),
        arrowstyle="->",
        color=MUTED,
        linewidth=1.25,
        mutation_scale=11,
    )
    time_arrow.set_sketch_params(scale=1.0, length=90.0, randomness=2.0)
    ax.add_patch(time_arrow)
    ax.text(
        0,
        3.73,
        "time",
        color=MUTED,
        fontsize=11.5 if mobile else 10.5,
        fontweight=600,
        va="bottom",
    )

    height = 0.34
    rows = (
        ("Fit 1", 3.02, 0.35),
        ("Fit 2", 2.18, 0.61),
        ("⋮", 1.50, None),
        ("Fit k", 0.82, 0.86),
    )
    for label, y, training_end in rows:
        ax.text(
            -0.15,
            y,
            label,
            color="#21334a",
            fontsize=12.0 if label == "⋮" else 11.0 if mobile else 10.5,
            fontweight=700,
            ha="left",
            va="center",
        )
        if training_end is None:
            continue
        track = FancyBboxPatch(
            (0, y - height / 2),
            1,
            height,
            boxstyle="round,pad=0.015,rounding_size=0.045",
            facecolor="#f3f5f6",
            edgecolor="#d4dadd",
            linewidth=1.0,
        )
        track.set_sketch_params(scale=1.0, length=95.0, randomness=2.0)
        ax.add_patch(track)
        training = FancyBboxPatch(
            (0, y - height / 2),
            training_end,
            height,
            boxstyle="round,pad=0.01,rounding_size=0.04",
            facecolor=TRAINING,
            edgecolor="#355b80",
            linewidth=1.1,
        )
        training.set_sketch_params(scale=1.0, length=80.0, randomness=2.2)
        ax.add_patch(training)
        gap = Rectangle(
            (training_end, y - height / 2 - 0.015),
            0.02,
            height + 0.03,
            facecolor=GAP,
            edgecolor="#625777",
            linewidth=1.0,
        )
        gap.set_sketch_params(scale=0.8, length=55.0, randomness=2.0)
        ax.add_patch(gap)
        test_width = min(0.23, 0.98 - training_end)
        test = FancyBboxPatch(
            (training_end + 0.02, y - height / 2),
            test_width,
            height,
            boxstyle="round,pad=0.01,rounding_size=0.04",
            facecolor=TEST,
            edgecolor="#63717d",
            linewidth=1.1,
        )
        test.set_sketch_params(scale=1.0, length=75.0, randomness=2.2)
        ax.add_patch(test)

    first_y = rows[0][1]
    first_training_end = rows[0][2]
    assert first_training_end is not None
    label_size = 8.8 if mobile else 9.2
    ax.text(
        first_training_end / 2,
        first_y,
        "Training history",
        color=WHITE,
        fontsize=label_size,
        fontweight=700,
        ha="center",
        va="center",
    )
    ax.text(
        first_training_end + 0.02 + 0.115,
        first_y,
        "Test block",
        color=WHITE,
        fontsize=label_size,
        fontweight=700,
        ha="center",
        va="center",
    )
    ax.annotate(
        "21-session gap",
        xy=(first_training_end + 0.01, first_y + height / 2),
        xytext=(first_training_end + 0.06, first_y + 0.48),
        color=GAP,
        fontsize=9.0 if mobile else 9.2,
        fontweight=600,
        ha="left",
        arrowprops={
            "arrowstyle": "->",
            "color": GAP,
            "linewidth": 1.0,
            "connectionstyle": "arc3,rad=0.18",
        },
    )
    note = (
        "Training history expands;\nonly the next block is scored."
        if mobile
        else "The training history expands; only the next block is scored."
    )
    ax.text(
        0,
        0.24 if mobile else 0.47,
        note,
        color=MUTED,
        fontsize=8.8 if mobile else 9.1,
        va="bottom",
    )
    if mobile:
        fig.subplots_adjust(left=0.18, right=0.98, top=0.98, bottom=0.08)
    else:
        fig.subplots_adjust(left=0.11, right=0.99, top=0.98, bottom=0.08)
    return fig


def save(fig: plt.Figure, stem: str, *, mobile: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "-mobile" if mobile else ""
    svg_path = OUTPUT_DIR / f"{stem}{suffix}.svg"
    fig.savefig(svg_path, format="svg", facecolor=WHITE)
    svg_path.write_text(
        "\n".join(
            line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()
        )
        + "\n",
        encoding="utf-8",
    )
    fig.savefig(OUTPUT_DIR / f"{stem}{suffix}.png", dpi=240, facecolor=WHITE)
    plt.close(fig)


def main() -> None:
    for mobile in (False, True):
        save(draw_walk_forward(mobile=mobile), "walk-forward", mobile=mobile)


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
