"""Generate matched OLS/Ridge article figures from retained compact evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from mlr_figures.diagnostics import plot_selected_coefficients
from mlr_figures.performance import plot_performance
from mlr_figures.structure import load_structure, plot_structure_figures
from mlr_figures.support import (
    FigureStyle,
    dark_figure_style,
    default_figure_spec,
    load_performance,
    load_selected_coefficients,
)


def default_output_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "multiple-linear-regression"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sources = parser.add_mutually_exclusive_group()
    sources.add_argument(
        "--research-root",
        type=Path,
        help="Path to the factor_combination research project.",
    )
    sources.add_argument(
        "--review-dir",
        type=Path,
        help="Exact compact evidence directory emitted by matched_model_review.py.",
    )
    parser.add_argument(
        "--structure-dir",
        type=Path,
        default=default_output_dir() / "evidence" / "predictor-structure",
        help="Evidence emitted by factor_combination/predictor_structure.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir(),
        help="Destination for the article SVG files.",
    )
    parser.add_argument(
        "--structure-only",
        action="store_true",
        help="Render only the predictor-structure figures.",
    )
    return parser.parse_args()


def figure_context(style: FigureStyle) -> dict[str, object]:
    return {
        "font.family": "DejaVu Sans",
        "axes.facecolor": style.white,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "svg.hashsalt": "multiple-linear-regression",
    }


def render_structure_figures(
    evidence_dir: Path, output_dir: Path, style: FigureStyle
) -> None:
    structure = load_structure(evidence_dir.resolve())
    with plt.rc_context(figure_context(style)):
        for mobile in (False, True):
            plot_structure_figures(structure, output_dir.resolve(), style, mobile=mobile)


def render_figures(
    review_dir: Path,
    output_dir: Path,
    style: FigureStyle,
) -> None:
    review_dir = review_dir.resolve()
    output_dir = output_dir.resolve()
    spec = default_figure_spec(style)
    wealth, drawdowns = load_performance(review_dir, spec.model_order)
    selected_coefficients = load_selected_coefficients(review_dir)
    # Load every required source before changing any published output.

    with plt.rc_context(figure_context(style)):
        plot_performance(wealth, drawdowns, output_dir, style, spec)
        plot_performance(wealth, drawdowns, output_dir, style, spec, mobile=True)
        plot_selected_coefficients(selected_coefficients, output_dir, style, spec)


def main() -> None:
    args = parse_args()
    styles = (FigureStyle(), dark_figure_style())
    for style in styles:
        render_structure_figures(args.structure_dir, args.output_dir, style)
    if args.structure_only:
        return
    if args.research_root is None and args.review_dir is None:
        raise SystemExit(
            "--review-dir or --research-root is required for the model figures"
        )
    review_dir = args.review_dir or args.research_root / "outputs" / "review"
    for style in styles:
        render_figures(review_dir, args.output_dir, style)


if __name__ == "__main__":
    main()
