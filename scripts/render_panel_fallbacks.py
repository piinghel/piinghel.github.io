"""Render static versions of the shrinkage and coefficient comparisons from their web data."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


def render(source: Path, key: str, base: Path, *, mobile: bool, dark: bool) -> None:
    chart = json.loads(source.read_text())["charts"][key]
    panels = chart["panels"]
    rows = (len(panels) + 1) // 2
    ink, grid, accent, paper = (
        ("#c9d1d9", "#36404a", "#89b5cc", "#0d1117") if dark else
        ("#27322f", "#e2e7eb", "#426e89", "#ffffff")
    )
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "svg.hashsalt": base.name}):
        fig, axes = plt.subplots(rows, 2, sharex=True, squeeze=False,
                                 figsize=(4.8 if mobile else 7.8, rows * 1.5 + .48))
        fig.patch.set_facecolor(paper)
        for axis, panel in zip(axes.flat, panels, strict=True):
            axis.set_facecolor(paper)
            axis.spines[:].set_visible(False)
            axis.grid(axis="y", color=grid, linewidth=.6)
            axis.set_axisbelow(True)
            axis.set_title(panel["title"], loc="left", color=ink, fontsize=10, pad=6)
            axis.plot(panel["x"], panel["y"], color=accent, marker="o", markersize=3, lw=1.3)
            if panel.get("reference") is not None:
                axis.axhline(panel["reference"], color=ink, lw=.7, linestyle=":", zorder=1)
            if "selected" in panel:
                selected = panel["x"].index(panel["selected"])
                axis.plot(panel["x"][selected], panel["y"][selected], marker="D",
                          color=ink, markersize=5)
            axis.set_yticks(panel["yTicks"])
            axis.set_ylim(panel["domain"])
            axis.set_xticks(panel["ticks"])
            axis.tick_params(length=0, labelsize=9, colors=ink, pad=3)
            axis.yaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
            axis.xaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
        fig.supxlabel(chart["sharedX"], fontsize=10, color=ink, y=.015)
        fig.subplots_adjust(left=.10 if mobile else .07, right=.98, top=1-.24/(rows*1.5+.48),
                            bottom=.47/(rows*1.5+.48), hspace=.55, wspace=.32)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        output = base.with_name(base.name + suffix + ".svg")
        fig.savefig(output, metadata={"Date": None})
        plt.close(fig)
        output.write_text("\n".join(line.rstrip() for line in output.read_text().splitlines()) + "\n")


def main(assets: Path) -> None:
    for source, key, name in (("joint-sizing/comparisons.json", "shrinkage", "rho-ladder"),
                              ("combining-predictors/coefficients.json", "stability", "refit-stability")):
        path = assets / source
        for dark in (False, True):
            for mobile in (False, True):
                render(path, key, path.with_name(name), mobile=mobile, dark=dark)


if __name__ == "__main__":
    main(Path(__file__).resolve().parents[1] / "assets")
