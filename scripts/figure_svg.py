"""File conventions for the blog's static Matplotlib figures."""

from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def svg_path(base: Path, *, mobile: bool, dark: bool) -> Path:
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    return base.with_name(f"{base.name}{suffix}.svg")


def save_svg(
    figure: Figure,
    path: Path,
    *,
    facecolor: str | None = None,
    transparent: bool | None = None,
    tight_padding: float | None = None,
) -> None:
    """Write a timestamp-free SVG with normalized whitespace and close the figure."""
    options = {}
    if facecolor is not None:
        options["facecolor"] = facecolor
    if tight_padding is not None:
        options.update(bbox_inches="tight", pad_inches=tight_padding)
    try:
        with StringIO() as svg:
            figure.savefig(
                svg, format="svg", metadata={"Date": None},
                transparent=transparent, **options,
            )
            path.write_text(
                "".join(f"{line.rstrip()}\n" for line in svg.getvalue().splitlines()),
                encoding="utf-8",
            )
    finally:
        plt.close(figure)
