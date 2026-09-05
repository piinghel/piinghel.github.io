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
        figsize=(4.8, 6.2) if mobile else (8.5, 6.4),
        facecolor=style.white,
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.22},
    )
    for axis in (wealth_ax, drawdown_ax):
        style_axis(
            axis,
            style,
            labelsize=10 if mobile else style.tick_label_size,
            grid_linewidth=0.55,
        )
    for model in spec.model_order:
        width = 1.25 if model == "fixed_factor_benchmark" else 1.5
        wealth_ax.plot(
            wealth[model].dates,
            wealth[model].values,
            color=spec.model_colors[model],
            linewidth=width,
            label=spec.model_labels[model],
        )
        drawdown_ax.plot(
            drawdowns[model].dates,
            drawdowns[model].values,
            color=spec.model_colors[model],
            linewidth=width - 0.45,
            label=spec.model_labels[model],
            zorder=2,
        )
        if model == "fixed_factor_benchmark":
            drawdown_ax.fill_between(
                drawdowns[model].dates,
                drawdowns[model].values,
                0,
                color=spec.model_colors[model],
                alpha=0.045,
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
    drawdown_ax.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
    drawdown_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    drawdown_ax.set_xlim(
        min(item.dates[0] for item in wealth.values()),
        max(item.dates[-1] for item in wealth.values()),
    )
    fig.subplots_adjust(
        left=0.14 if mobile else 0.10,
        right=0.79 if mobile else 0.84,
        top=0.93,
        bottom=0.06,
    )
    # Label the paths in the margin, separating their close endpoints without
    # changing either the data or the time axis.
    fig.canvas.draw()
    ordered = sorted(spec.model_order, key=lambda model: wealth[model].values[-1])
    endpoint_pixels = [
        wealth_ax.transData.transform(
            (mdates.date2num(wealth[model].dates[-1]), wealth[model].values[-1])
        )[1]
        for model in ordered
    ]
    gap_pixels = (13 if mobile else 12) * fig.dpi / 72
    label_pixels = [endpoint_pixels[0]]
    for endpoint in endpoint_pixels[1:]:
        label_pixels.append(max(endpoint, label_pixels[-1] + gap_pixels))
    center_shift = sum(
        label - endpoint for label, endpoint in zip(label_pixels, endpoint_pixels)
    ) / len(ordered)
    for model, endpoint, label in zip(ordered, endpoint_pixels, label_pixels):
        wealth_ax.annotate(
            (
                "Fixed" if mobile and model == "fixed_factor_benchmark"
                else spec.model_labels[model]
            ),
            xy=(wealth[model].dates[-1], wealth[model].values[-1]),
            xytext=(8, (label - center_shift - endpoint) * 72 / fig.dpi),
            textcoords="offset points",
            va="center",
            color=spec.model_colors[model],
            fontsize=10 if mobile else style.legend_size,
            arrowprops={
                "arrowstyle": "-",
                "color": spec.model_colors[model],
                "lw": 0.6,
                "shrinkA": 1,
                "shrinkB": 2,
            },
            annotation_clip=False,
        )
    stem = "performance-and-drawdowns_mobile" if mobile else "performance-and-drawdowns"
    save_figure(fig, output_dir, stem, style)
