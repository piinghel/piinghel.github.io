"""Render the regression article's static predictor-structure figures.

They are the no-JavaScript fallback of the interactive Figure 1 and read the compact
evidence in assets/multiple-linear-regression/evidence/predictor-structure.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from mlr_figures.structure import load_structure, plot_structure_figures
from mlr_figures.support import FigureStyle, dark_figure_style

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "multiple-linear-regression"


def figure_context(style: FigureStyle) -> dict[str, object]:
    return {
        "font.family": "DejaVu Sans",
        "axes.facecolor": style.white,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "svg.hashsalt": "multiple-linear-regression",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--structure-dir", type=Path, default=ASSETS / "evidence" / "predictor-structure")
    parser.add_argument("--output-dir", type=Path, default=ASSETS)
    args = parser.parse_args()
    structure = load_structure(args.structure_dir.resolve())
    for style in (FigureStyle(), dark_figure_style()):
        with plt.rc_context(figure_context(style)):
            for mobile in (False, True):
                plot_structure_figures(structure, args.output_dir.resolve(), style, mobile=mobile)


if __name__ == "__main__":
    main()
