"""Render the rebalance schedules and their mixture from aggregate daily returns."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, NullFormatter, StrMethodFormatter


def render(
    rows: list[dict[str, str]], output: Path, *, dark: bool, mobile: bool = False
) -> None:
    ink, grid = ("#c9d1d9", "#30363d") if dark else ("#33404b", "#dbe1e3")
    colors = (
        ["#8097ad", "#c79261", "#89a88c", "#e7edf1"]
        if dark
        else ["#708da7", "#b98556", "#86a488", "#263e54"]
    )
    with plt.rc_context(
        {
            "font.family": ["DejaVu Sans", "sans-serif"],
            "font.size": 11,
            "svg.fonttype": "none",
            "svg.hashsalt": "timing-performance",
        }
    ):
        fig, ax = plt.subplots(figsize=(4.8, 4.8) if mobile else (8.5, 4.8))
        fig.patch.set_alpha(0)
        handles = []
        sample = [row for row in rows if row["period"] == "later"]
        dates = [date.fromisoformat(row["date"]) for row in sample]
        dates = [dates[0] - timedelta(days=1), *dates]
        for index, key in enumerate(("week_1", "week_2", "week_3", "mixture")):
            returns = np.array([float(row[key]) for row in sample])
            growth = np.r_[1.0, np.cumprod(1 + returns)]
            (line,) = ax.plot(
                dates, growth, color=colors[index], linewidth=2.1 if index == 3 else 1.1
            )
            handles.append(line)
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(FixedLocator([1, 1.2, 1.4, 1.6]))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_ylabel("Net growth index (log scale)", color=ink)
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.grid(axis="y", which="major", color=grid, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.patch.set_alpha(0)
        ax.tick_params(axis="both", which="both", colors=ink, length=0, pad=7)
        ax.margins(x=0, y=0.06)
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.legend(
            handles,
            ["Sleeve A", "Sleeve B", "Sleeve C", "Three-sleeve mixture"],
            loc="lower center",
            ncol=2 if mobile else 4,
            frameon=False,
            labelcolor=ink,
            bbox_to_anchor=(0.53, 0.005),
        )
        fig.subplots_adjust(
            left=0.16 if mobile else 0.10,
            right=0.975,
            top=0.96,
            bottom=0.23 if mobile else 0.19,
        )
        fig.savefig(output, transparent=True, metadata={"Date": None})
        output.write_text(
            "\n".join(line.rstrip() for line in output.read_text().splitlines()) + "\n"
        )
        plt.close(fig)


def main() -> None:
    assets = Path(__file__).resolve().parents[1] / "assets/tranching"
    with (assets / "schedule_returns.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    for dark in (False, True):
        for mobile in (False, True):
            render(
                rows,
                assets
                / f"schedule-performance{'_mobile' if mobile else ''}{'_dark' if dark else ''}.svg",
                dark=dark,
                mobile=mobile,
            )


if __name__ == "__main__":
    main()
