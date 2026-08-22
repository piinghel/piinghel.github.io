"""Prediction and portfolio-performance figures for the regression article."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

from mlr_figure_support import (
    FigureSpec,
    FigureStyle,
    Series,
    add_split_marker,
    save_figure,
    style_axis,
)


def plot_ic(
    series: dict[str, Series],
    output_dir: Path,
    style: FigureStyle,
    spec: FigureSpec,
    *,
    mobile: bool,
) -> None:
    size = (4.6, 5.1) if mobile else (10.2, 5.5)
    fig, ax = plt.subplots(figsize=size, facecolor=style.white)
    for model in spec.model_order:
        values = np.cumsum(series[model].values)
        ax.plot(
            series[model].dates,
            values,
            color=spec.model_colors[model],
            linewidth=2.0 if model == "selected_c0p01" else 1.6,
        )
        offset = {
            "fixed_factor_benchmark": -10,
            "ols_c0": 2,
            "selected_c0p01": 10,
        }[model]
        ax.annotate(
            spec.model_labels[model],
            (series[model].dates[-1], values[-1]),
            xytext=(7, offset),
            textcoords="offset points",
            color=(
                style.muted
                if model == "fixed_factor_benchmark"
                else spec.model_colors[model]
            ),
            fontsize=style.legend_size,
            fontweight=600 if model == "selected_c0p01" else 400,
            va="center",
        )
    style_axis(ax, style)
    add_split_marker(
        ax,
        style,
        spec.split_date,
        label=True,
        label_fontsize=style.annotation_size,
        label_text="Model fixed before 2022",
        label_at_top=True,
    )
    ax.set_ylabel(
        "Cumulative daily rank IC",
        color=style.muted,
        fontsize=style.axis_label_size * 1.2,
    )
    ax.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    right = series[spec.model_order[0]].dates[-1] + timedelta(
        days=780 if mobile else 520
    )
    ax.set_xlim(series[spec.model_order[0]].dates[0], right)
    fig.subplots_adjust(
        left=0.16 if mobile else 0.10,
        right=0.82 if mobile else 0.87,
        top=0.97,
        bottom=0.12,
    )
    save_figure(fig, output_dir, "cumulative-ic", style, mobile=mobile)


def plot_performance(
    wealth: dict[str, Series],
    drawdowns: dict[str, Series],
    output_dir: Path,
    style: FigureStyle,
    spec: FigureSpec,
    *,
    mobile: bool,
) -> None:
    size = (4.6, 7.2) if mobile else (10.8, 6.7)
    fig, (wealth_ax, drawdown_ax) = plt.subplots(
        2,
        1,
        figsize=size,
        facecolor=style.white,
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.04},
    )
    for axis in (wealth_ax, drawdown_ax):
        style_axis(axis, style)
        add_split_marker(
            axis,
            style,
            spec.split_date,
            label=axis is wealth_ax,
            label_fontsize=style.annotation_size,
            label_text="Model fixed before 2022",
            label_at_top=True,
        )
    for model in spec.model_order:
        width = 2.0 if model == "selected_c0p01" else 1.5
        wealth_ax.plot(
            wealth[model].dates,
            wealth[model].values,
            color=spec.model_colors[model],
            linewidth=width,
        )
        drawdown_ax.plot(
            drawdowns[model].dates,
            drawdowns[model].values,
            color=spec.model_colors[model],
            linewidth=width - 0.2,
            zorder=2,
        )
        drawdown_ax.fill_between(
            drawdowns[model].dates,
            drawdowns[model].values,
            0,
            color=spec.model_colors[model],
            alpha=0.035,
            linewidth=0,
            rasterized=True,
            zorder=1,
        )
        offset = {
            "fixed_factor_benchmark": -10,
            "ols_c0": 0,
            "selected_c0p01": 10,
        }[model]
        wealth_ax.annotate(
            spec.model_labels[model],
            (wealth[model].dates[-1], wealth[model].values[-1]),
            xytext=(7, offset),
            textcoords="offset points",
            color=spec.model_colors[model],
            fontsize=style.legend_size,
            fontweight=600 if model == "selected_c0p01" else 400,
            va="center",
        )
    wealth_ax.set_yscale("log")
    wealth_ax.set_ylabel(
        "Growth of $1",
        color=style.muted,
        fontsize=style.axis_label_size,
    )
    wealth_ax.yaxis.set_major_locator(FixedLocator([1, 2, 3, 4, 6, 8]))
    wealth_ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}×"))
    wealth_ax.yaxis.set_minor_formatter(NullFormatter())
    wealth_ax.grid(False, axis="y")
    for value in (1, 2, 3, 4, 6, 8):
        wealth_ax.axhline(value, color=style.grid, linewidth=0.8, zorder=0)
    drawdown_ax.set_ylabel(
        "Drawdown (%)",
        color=style.muted,
        fontsize=style.axis_label_size,
    )
    drawdown_ax.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 4))
    drawdown_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    right = wealth[spec.model_order[0]].dates[-1] + timedelta(
        days=780 if mobile else 520
    )
    drawdown_ax.set_xlim(wealth[spec.model_order[0]].dates[0], right)
    fig.subplots_adjust(
        left=0.17 if mobile else 0.10,
        right=0.82 if mobile else 0.87,
        top=0.98,
        bottom=0.08,
    )
    save_figure(
        fig,
        output_dir,
        "performance-and-drawdowns",
        style,
        mobile=mobile,
    )
