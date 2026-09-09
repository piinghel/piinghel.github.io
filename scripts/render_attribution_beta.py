"""Render aggregate portfolio beta history, with one composition per viewport."""

import datetime as dt
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"


def render(data, dark, mobile):
    colors = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4eaf0" if dark else "#263747",
        "grid": "#43505f" if dark else "#d6dfe5",
        "beta": "#76b3d4" if dark else "#32759a",
        "model": "#e6ae70" if dark else "#ad702c",
    }
    dates = [dt.date.fromisoformat(value) for value in data["dates"]]
    with plt.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "svg.hashsalt": "attribution-beta",
        }
    ):
        fig, axes = plt.subplots(
            2, 1, sharex=True, figsize=(4, 5.6) if mobile else (9.6, 5.5)
        )
        fig.set_facecolor(colors["bg"])
        for ax, key, title, color in zip(
            axes,
            ["realized_beta", "model_beta"],
            [
                "Realized market beta · trailing year",
                "Model beta exposure · per notional",
            ],
            [colors["beta"], colors["model"]],
        ):
            values = np.array(
                [np.nan if value is None else value for value in data[key]]
            )
            ax.set_facecolor(colors["bg"])
            ax.spines[:].set_visible(False)
            ax.plot(dates, values, color=color, linewidth=1.1)
            ax.axhline(0, color=colors["grid"], linewidth=0.8)
            ax.grid(axis="y", color=colors["grid"], linewidth=0.5, alpha=0.6)
            ax.set_axisbelow(True)
            ax.set_title(
                title,
                loc="left",
                color=colors["ink"],
                fontsize=10.5 if mobile else 12,
                weight="semibold",
                pad=12,
            )
            ax.tick_params(
                colors=colors["ink"], labelsize=10 if mobile else 11, length=0, pad=6
            )
            for row in data["lows"]:
                date = dt.date.fromisoformat(row["date"])
                ax.axvline(date, color=colors["grid"], linewidth=0.8, linestyle="--")
                ax.scatter(date, row[key], s=20, color=color, zorder=4)
            ax.margins(y=0.16)
            ax.set_xlim(dates[0], dates[-1])
            ax.yaxis.set_major_locator(plt.MaxNLocator(4))
        for row in data["lows"]:
            axes[0].text(
                mdates.date2num(dt.date.fromisoformat(row["date"])),
                0.97,
                row["date"][:4],
                transform=axes[0].get_xaxis_transform(),
                fontsize=9,
                color=colors["ink"],
                ha="center",
                va="top",
            )
        axes[1].xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        fig.subplots_adjust(
            left=0.17 if mobile else 0.085,
            right=0.97,
            top=0.91,
            bottom=0.08,
            hspace=0.56,
        )
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        fig.savefig(OUTPUT / f"beta-history{suffix}.svg", metadata={"Date": None})
        plt.close(fig)


if __name__ == "__main__":
    data = json.loads((OUTPUT / "beta-history.json").read_text())
    for dark in [False, True]:
        for mobile in [False, True]:
            render(data, dark, mobile)
