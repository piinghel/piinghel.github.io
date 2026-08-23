"""Generate the walk-forward article figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "multiple-linear-regression"
MUTED = "#66737e"
WHITE = "#ffffff"
TRAINING = "#417795"
GAP = "#ca7069"
TEST = "#409b93"


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
        ("Fit …", 1.50, None),
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
        if training_end is None:
            continue
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
    for mobile in (False, True):
        save(draw_walk_forward(mobile=mobile), "walk-forward", mobile=mobile)


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": WHITE, "savefig.bbox": "tight", "savefig.pad_inches": 0.04})
    main()
