"""Prediction and portfolio-performance figures for the regression article."""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from .support import (
    FigureSpec,
    FigureStyle,
    Series,
    add_panel_title,
    add_split_marker,
    save_figure,
    style_axis,
)


def plot_performance(
    wealth: dict[str, Series],
    drawdowns: dict[str, Series],
    output_dir: Path,
    style: FigureStyle,
    spec: FigureSpec,
    *,
    mobile: bool = False,
) -> None:
    fig, (wealth_ax, drawdown_ax) = plt.subplots(
        2,
        1,
        figsize=(4.8, 6.2) if mobile else (8.5, 6.7),
        facecolor=style.white,
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.24},
    )
    for axis in (wealth_ax, drawdown_ax):
        style_axis(
            axis,
            style,
            labelsize=10 if mobile else style.tick_label_size,
            grid_linewidth=0.55,
        )
        add_split_marker(
            axis,
            style,
            spec.split_date,
        )
    for model in spec.model_order:
        width = 1.25 if model == "fixed_factor_benchmark" else 1.5
        line_style = (0, (5, 2.5)) if model == "selected_c0p01" else "solid"
        wealth_ax.plot(
            wealth[model].dates,
            wealth[model].values,
            color=spec.model_colors[model],
            linewidth=width,
            linestyle=line_style,
            label=spec.model_labels[model],
        )
        drawdown_ax.plot(
            drawdowns[model].dates,
            drawdowns[model].values,
            color=spec.model_colors[model],
            linewidth=width - 0.2,
            linestyle=line_style,
            label=spec.model_labels[model],
            zorder=2,
        )
        if model == "fixed_factor_benchmark":
            drawdown_ax.fill_between(
                drawdowns[model].dates,
                drawdowns[model].values,
                0,
                color=spec.model_colors[model],
                alpha=0.07,
                linewidth=0,
                zorder=1,
            )
    wealth_ax.set_yscale("log")
    panel_title_color = "#000000" if not style.output_suffix else style.ink
    add_panel_title(
        wealth_ax,
        "Net growth index (log scale)",
        color=panel_title_color,
        fontsize=12 if mobile else style.axis_label_size,
        fontweight="semibold",
    )
    wealth_ax.yaxis.set_major_locator(LogLocator(base=2, subs=(1.0,)))
    wealth_ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}×"))
    wealth_ax.yaxis.set_minor_formatter(NullFormatter())
    wealth_ax.axhline(1, color=style.muted, linewidth=0.6, zorder=0)
    drawdown_ax.axhline(0, color=style.muted, linewidth=0.6, zorder=0)
    add_panel_title(
        drawdown_ax,
        "Drawdown (%)",
        color=panel_title_color,
        fontsize=12 if mobile else style.axis_label_size,
        fontweight="semibold",
    )
    drawdown_ax.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 4))
    drawdown_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    drawdown_ax.set_xlim(
        min(item.dates[0] for item in wealth.values()),
        max(item.dates[-1] for item in wealth.values()),
    )
    fig.legend(
        *wealth_ax.get_legend_handles_labels(),
        loc="upper center",
        ncol=3,
        frameon=False,
        labelcolor=style.ink,
        fontsize=10 if mobile else style.legend_size,
        bbox_to_anchor=(0.55, 1.0),
        handlelength=2.5,
        columnspacing=1.4,
    )
    fig.subplots_adjust(
        left=0.14 if mobile else 0.10,
        right=0.98,
        top=0.90,
        bottom=0.06,
    )
    stem = "performance-and-drawdowns_mobile" if mobile else "performance-and-drawdowns"
    save_figure(fig, output_dir, stem, style)
