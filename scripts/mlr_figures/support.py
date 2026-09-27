"""Style and SVG output shared by the regression article's static figures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class FigureStyle:
    ink: str = "#33404b"
    muted: str = "#6a7883"
    white: str = "#ffffff"
    heat_negative: str = "#9A4E22"
    heat_positive: str = "#2E5B82"
    output_suffix: str = ""


def dark_figure_style() -> FigureStyle:
    """Match the figures to the website's dark surface."""
    return FigureStyle(
        ink="#C9D1D9",
        muted="#8B949E",
        white="#0D1117",
        heat_negative="#E3A574",
        heat_positive="#8DB8DE",
        output_suffix="_dark",
    )


def save_figure(
    fig: plt.Figure,
    output_dir: Path,
    stem: str,
    style: FigureStyle,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_path = output_dir / f"{stem}{style.output_suffix}.svg"
    fig.savefig(
        svg_path,
        format="svg",
        facecolor=style.white,
        metadata={"Date": None},
    )
    lines = svg_path.read_text(encoding="utf-8").splitlines()
    svg_path.write_text(
        "\n".join(line.rstrip() for line in lines) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
