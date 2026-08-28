"""Generate matched OLS/Ridge article figures from retained compact evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from mlr_figures.diagnostics import (
    plot_alpha_sensitivity,
    plot_portfolio_exposures,
    plot_selected_coefficients,
    plot_selected_portfolio_tilts,
    plot_turnover_costs,
)
from mlr_figures.performance import plot_ic, plot_performance
from mlr_figures.support import (
    FigureStyle,
    Series,
    dark_figure_style,
    default_figure_spec,
    load_alpha_diagnostics,
    load_daily_series,
    load_selected_coefficients,
    load_selected_exposures,
    load_selected_portfolio_tilts,
    read_rows,
)


def default_output_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "multiple-linear-regression"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--research-root",
        type=Path,
        required=True,
        help="Path to the factor_combination research project.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir(),
        help="Destination for the article SVG files.",
    )
    return parser.parse_args()


def render_figures(
    research_root: Path,
    output_dir: Path,
    style: FigureStyle,
) -> None:
    review_dir = research_root.resolve() / "outputs" / "review"
    output_dir = output_dir.resolve()
    spec = default_figure_spec(style)
    ic = load_daily_series(
        review_dir / "multiple_linear_selected_daily_ic_figure_source.csv.gz",
        value_column="daily_rank_ic",
        model_order=spec.model_order,
    )
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
    diagnostics = load_alpha_diagnostics(
        review_dir,
        alpha_models=spec.alpha_models,
    )
    period_metrics = read_rows(
        review_dir / "multiple_linear_period_portfolio_metrics.csv"
    )
    selected_coefficients = load_selected_coefficients(review_dir)
    selected_exposures = load_selected_exposures(review_dir)
    selected_portfolio_tilts = load_selected_portfolio_tilts(review_dir)

    with plt.rc_context(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": style.white,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "svg.hashsalt": "multiple-linear-regression",
        }
    ):
        plot_ic(ic, output_dir, style, spec)
        plot_performance(wealth, drawdowns, output_dir, style, spec)
        plot_alpha_sensitivity(diagnostics, output_dir, style, spec)
        plot_selected_coefficients(selected_coefficients, output_dir, style, spec)
        plot_portfolio_exposures(selected_exposures, output_dir, style)
        plot_selected_portfolio_tilts(
            selected_portfolio_tilts,
            output_dir,
            style,
            spec,
        )
        plot_turnover_costs(period_metrics, output_dir, style)


def main() -> None:
    args = parse_args()
    render_figures(args.research_root, args.output_dir, FigureStyle())
    render_figures(args.research_root, args.output_dir, dark_figure_style())


if __name__ == "__main__":
    main()
