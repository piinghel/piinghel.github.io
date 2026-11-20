"""Render the predictor article's fallback from its published decile returns."""

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from blog_charts import statistics
from matplotlib.ticker import PercentFormatter


@dataclass(frozen=True)
class DecilePeriod:
    label: str
    ridge: tuple[float, ...]
    equal_weight: tuple[float, ...]


def read_periods(source: Path) -> list[DecilePeriod]:
    chart = json.loads(source.read_text())
    values = {series["id"]: series["values"] for series in chart["series"]}
    periods = []
    for label, start, end in chart["charts"]["deciles"]["episodes"][:2]:
        sessions = [
            index for index, day in enumerate(chart["dates"]) if start <= day <= end
        ]
        annual_returns = {
            model: tuple(
                statistics(
                    [
                        values[f"{model}_{decile}"][index] / chart["scale"]
                        for index in sessions
                    ],
                    annualization=chart["annualization"],
                )["annual_return"]
                for decile in range(1, 11)
            )
            for model in ("ridge", "equal_weight")
        }
        periods.append(DecilePeriod(label, **annual_returns))
    return periods


def render(
    periods: list[DecilePeriod], destination: Path, *, mobile: bool, dark: bool
) -> None:
    ink = "#e4e7ea" if dark else "#25313a"
    ridge = "#81b4f3" if dark else "#2262ab"
    neutral = "#aab3bf" if dark else "#596877"
    grid = "#313843" if dark else "#e2e7ed"
    with plt.rc_context(
        {"font.family": "DejaVu Sans", "svg.hashsalt": "predictor-deciles"}
    ):
        figure, axes = plt.subplots(
            *((2, 1) if mobile else (1, 2)),
            figsize=(4.45, 5.65) if mobile else (8.4, 3.2),
            sharey=True,
        )
        figure.subplots_adjust(
            left=0.14 if mobile else 0.09,
            right=0.97,
            top=0.92 if mobile else 0.83,
            bottom=0.15 if mobile else 0.25,
            hspace=0.55,
        )
        deciles = range(1, 11)
        for axis, period in zip(axes, periods, strict=True):
            axis.plot(
                deciles, period.ridge, "o-", color=ridge, label="Ridge", markersize=3.8
            )
            axis.plot(
                deciles,
                period.equal_weight,
                "s--",
                color=neutral,
                label="Equal-weight score",
                markersize=3.2,
            )
            axis.set_title(period.label, loc="left", color=ink, fontsize=10)
            axis.set_xticks([1, 3, 5, 7, 10])
            axis.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
            axis.grid(axis="y", color=grid, linewidth=0.7)
            axis.axhline(0, color=neutral, linewidth=0.7)
            axis.set_axisbelow(True)
            axis.spines[:].set_visible(False)
            axis.tick_params(
                length=0, colors=ink, labelsize=9, labelleft=mobile or axis is axes[0]
            )
        axes[0].set_ylabel("Annual return", color=ink, fontsize=9)
        if mobile:
            axes[-1].set_ylabel("Annual return", color=ink, fontsize=9)
        figure.supxlabel(
            "Score decile", y=0.08 if mobile else 0.13, color=ink, fontsize=9
        )
        figure.legend(
            *axes[0].get_legend_handles_labels(),
            loc="lower center",
            ncol=2,
            frameon=False,
            fontsize=9,
            labelcolor=ink,
        )
        figure.savefig(destination, transparent=True, metadata={"Date": None})
        plt.close(figure)
    destination.write_text(
        "".join(f"{line.rstrip()}\n" for line in destination.read_text().splitlines())
    )


if __name__ == "__main__":
    assets = Path(__file__).resolve().parents[1] / "assets" / "combining-predictors"
    decile_periods = read_periods(assets / "deciles.json")
    for mobile in (False, True):
        for dark in (False, True):
            suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
            render(
                decile_periods,
                assets / f"decile-returns{suffix}.svg",
                mobile=mobile,
                dark=dark,
            )
