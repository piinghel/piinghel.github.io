"""Static predictor-structure figures (the explorer's no-JavaScript fallback): theme-ordered
correlations and theme IC by year."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from .support import FigureStyle, save_figure

SHORT_THEME_LABELS: dict[str, str] = {
    "Momentum & trend": "Momentum",
    "Short-term reversal": "Reversal",
    "Volatility": "Volatility",
    "Size": "Size",
    "Liquidity & volume": "Liquidity",
    "Market correlation": "Mkt corr.",
    "Short positioning": "Shorts",
}


@dataclass(frozen=True)
class PredictorStructure:
    """Compact evidence written by factor_combination/predictor_structure.py."""

    themes: tuple[str, ...]  # theme of each predictor, in matrix order
    correlation: np.ndarray  # (k, k) IC-signed average rank correlations
    theme_pairs: pl.DataFrame  # year, theme_a, theme_b, rho
    theme_ic: pl.DataFrame  # year, theme, ic


def load_structure(evidence_dir: Path) -> PredictorStructure:
    predictors = pl.read_csv(evidence_dir / "predictors.csv")
    matrix = pl.read_csv(evidence_dir / "predictor_correlation.csv")
    if matrix.columns != predictors.get_column("predictor").to_list():
        raise ValueError("correlation columns must follow the predictor order")
    correlation = matrix.to_numpy()
    if (
        not np.isfinite(correlation).all()
        or not np.allclose(correlation, correlation.T, atol=1e-5)
        or not np.allclose(np.diag(correlation), 1.0, atol=1e-5)
    ):
        raise ValueError("predictor correlations must be finite, symmetric, unit diagonal")
    themes = tuple(predictors.get_column("theme").to_list())
    theme_pairs = pl.read_csv(evidence_dir / "theme_correlation_yearly.csv")
    theme_ic = pl.read_csv(evidence_dir / "theme_ic_yearly.csv")
    known = set(themes)
    for frame, columns in ((theme_pairs, ("theme_a", "theme_b")), (theme_ic, ("theme",))):
        seen = {t for c in columns for t in frame.get_column(c).unique().to_list()}
        if seen != known:
            raise ValueError(f"yearly evidence themes {sorted(seen)} != {sorted(known)}")
    return PredictorStructure(themes, correlation, theme_pairs, theme_ic)


def plot_structure_figures(
    structure: PredictorStructure,
    output_dir: Path,
    style: FigureStyle,
    *,
    mobile: bool,
) -> None:
    suffix = "_mobile" if mobile else ""
    plot_predictor_correlation(structure, output_dir, style, stem=f"predictor-correlation{suffix}", mobile=mobile)
    plot_theme_ic(structure, output_dir, style, stem=f"theme-ic-by-year{suffix}", mobile=mobile)


def plot_predictor_correlation(
    structure: PredictorStructure,
    output_dir: Path,
    style: FigureStyle,
    *,
    stem: str,
    mobile: bool,
    short_labels: Mapping[str, str] = SHORT_THEME_LABELS,
) -> None:
    """Average correlation of every predictor pair, grouped into theme blocks."""
    matrix = structure.correlation
    k = matrix.shape[0]
    fig, ax = plt.subplots(
        figsize=(4.8, 5.0) if mobile else (8.4, 7.2), facecolor=style.white
    )
    mesh = ax.pcolormesh(
        np.arange(k + 1),
        np.arange(k + 1),
        matrix,
        cmap=_diverging(style),
        norm=TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0),
        shading="flat",
    )
    ax.set_xlim(0, k)
    ax.set_ylim(k, 0)
    ax.set_aspect("equal")
    starts, ends, names = _blocks(structure.themes)
    for boundary in starts[1:]:
        ax.axhline(boundary, color=style.white, linewidth=1.4)
        ax.axvline(boundary, color=style.white, linewidth=1.4)
    centers = [(a + b) / 2 for a, b in zip(starts, ends)]
    names_shown = [short_labels[n] if mobile else n for n in names]
    ax.set_yticks(centers, names_shown)
    ax.set_xticks([])
    ax.tick_params(
        axis="y", length=0, colors=style.ink, labelsize=9.5 if mobile else 10
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    colorbar = fig.colorbar(
        mesh,
        ax=ax,
        orientation="horizontal",
        fraction=0.04,
        pad=0.03,
        aspect=30,
        ticks=[-1, -0.5, 0, 0.5, 1],
    )
    _style_colorbar(colorbar, style, "Average rank correlation (IC-signed)")
    save_figure(fig, output_dir, stem, style)


def plot_theme_ic(
    structure: PredictorStructure,
    output_dir: Path,
    style: FigureStyle,
    *,
    stem: str,
    mobile: bool,
    short_labels: Mapping[str, str] = SHORT_THEME_LABELS,
    limit: float = 0.12,
) -> None:
    """Mean daily rank IC of each theme composite with the target, by year."""
    themes = list(dict.fromkeys(structure.themes))
    years, values = _pivot(structure.theme_ic, rows=themes, row_column="theme", value="ic")
    if np.abs(values).max() > limit:
        raise ValueError(f"theme IC exceeds the colour limit {limit}")
    names = [short_labels[t] if mobile else t for t in themes]
    fig, ax = plt.subplots(
        figsize=(4.8, 3.4) if mobile else (8.6, 3.3), facecolor=style.white
    )
    mesh = _year_heatmap(ax, values, years, names, style, limit=limit, mobile=mobile)
    colorbar = fig.colorbar(
        mesh, ax=ax, orientation="horizontal", fraction=0.07, pad=0.2 if mobile else 0.17,
        aspect=30, ticks=[-limit, -limit / 2, 0, limit / 2, limit],
    )
    _style_colorbar(colorbar, style, "Mean daily rank IC")
    save_figure(fig, output_dir, stem, style)


def _blocks(themes: Sequence[str]) -> tuple[list[int], list[int], list[str]]:
    """Start, end and name of each run of equal consecutive themes."""
    starts, names = [], []
    for i, theme in enumerate(themes):
        if i == 0 or theme != themes[i - 1]:
            starts.append(i)
            names.append(theme)
    if len(set(names)) != len(names):
        raise ValueError("each theme's predictors must be contiguous")
    return starts, starts[1:] + [len(themes)], names


def _pivot(
    frame: pl.DataFrame, *, rows: Sequence[str], row_column: str, value: str
) -> tuple[list[int], np.ndarray]:
    years = sorted(frame.get_column("year").unique().to_list())
    wide = frame.pivot(on="year", index=row_column, values=value)
    wide = pl.DataFrame({row_column: list(rows)}).join(wide, on=row_column, how="left")
    values = wide.select([str(y) for y in years]).to_numpy().astype(float)
    if not np.isfinite(values).all():
        raise ValueError(f"missing {value} values in the yearly evidence")
    return years, values


def _year_heatmap(
    ax: plt.Axes,
    values: np.ndarray,
    years: Sequence[int],
    rows: Sequence[str],
    style: FigureStyle,
    *,
    limit: float,
    mobile: bool,
):
    mesh = ax.pcolormesh(
        np.arange(len(years) + 1),
        np.arange(len(rows) + 1),
        values,
        cmap=_diverging(style),
        norm=TwoSlopeNorm(vmin=-limit, vcenter=0.0, vmax=limit),
        shading="flat",
        edgecolors=style.white,
        linewidth=0.6,
    )
    ax.set_xlim(0, len(years))
    ax.set_ylim(len(rows), 0)
    step = 5
    ticks = [i for i, y in enumerate(years) if y % step == 0]
    ax.set_xticks(
        [t + 0.5 for t in ticks],
        [str(years[t]) if not mobile else f"’{years[t] % 100:02d}" for t in ticks],
    )
    ax.set_yticks(np.arange(len(rows)) + 0.5, rows)
    ax.tick_params(axis="both", length=0, labelsize=9.5 if mobile else 10)
    ax.tick_params(axis="x", colors=style.muted)
    ax.tick_params(axis="y", colors=style.ink)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return mesh


def _diverging(style: FigureStyle) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(
        "diverging", (style.heat_negative, style.white, style.heat_positive)
    )


def _style_colorbar(colorbar, style: FigureStyle, label: str) -> None:
    colorbar.solids.set_rasterized(False)
    colorbar.outline.set_visible(False)
    colorbar.set_label(label, color=style.ink, fontsize=9.5)
    colorbar.ax.tick_params(colors=style.muted, labelsize=9, length=0)
