"""Generate matched OLS/Ridge article figures from retained compact evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from mlr_figures.diagnostics import (
    plot_factor_correlation,
    plot_selected_coefficients,
)
from mlr_figures.performance import plot_performance
from mlr_figures.support import (
    FigureStyle,
    Series,
    dark_figure_style,
    default_figure_spec,
    load_daily_series,
    load_selected_coefficients,
    read_rows,
)


def default_output_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "multiple-linear-regression"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--research-root",
        type=Path,
        help="Path to the factor_combination research project.",
    )
    parser.add_argument(
        "--correlation-source",
        type=Path,
        help="Explicit matrix CSV for the correlation-only renderer.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir(),
        help="Destination for the article SVG files.",
    )
    parser.add_argument(
        "--factor-correlation-only",
        action="store_true",
        help="Render only the five-factor development correlation comparison.",
    )
    return parser.parse_args()


def render_factor_correlation(
    source: Path,
    output_dir: Path,
    style: FigureStyle,
) -> None:
    rows = read_rows(source)
    with plt.rc_context(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": style.white,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "svg.hashsalt": "multiple-linear-regression",
        }
    ):
        plot_factor_correlation(rows, output_dir.resolve(), style)


def render_figures(
    research_root: Path,
    output_dir: Path,
    style: FigureStyle,
) -> None:
    review_dir = research_root.resolve() / "outputs" / "review"
    output_dir = output_dir.resolve()
    spec = default_figure_spec(style)
    wealth = load_daily_series(
        review_dir / "multiple_linear_selected_return_drawdown_figure_source.csv.gz",
        value_column="cumulative_net_return_pct",
        model_order=spec.model_order,
    )
    wealth = {
        model: Series(item.dates, 1.0 + item.values / 100.0)
        for model, item in wealth.items()
    }
    drawdowns = load_daily_series(
        review_dir / "multiple_linear_selected_return_drawdown_figure_source.csv.gz",
        value_column="drawdown_pct",
        model_order=spec.model_order,
    )
    selected_coefficients = load_selected_coefficients(review_dir)
    # Load every required source before changing any published output.

    with plt.rc_context(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": style.white,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "svg.hashsalt": "multiple-linear-regression",
        }
    ):
        plot_performance(wealth, drawdowns, output_dir, style, spec)
        plot_selected_coefficients(selected_coefficients, output_dir, style, spec)


def main() -> None:
    args = parse_args()
    if args.factor_correlation_only:
        source = (
            args.correlation_source or default_output_dir() / "factor-correlations.csv"
        )
        render_factor_correlation(
            source,
            args.output_dir,
            FigureStyle(),
        )
        render_factor_correlation(
            source,
            args.output_dir,
            dark_figure_style(),
        )
        return
    if args.research_root is None:
        raise SystemExit("--research-root is required for the full figure set")
    render_figures(args.research_root, args.output_dir, FigureStyle())
    render_figures(args.research_root, args.output_dir, dark_figure_style())


if __name__ == "__main__":
    main()
