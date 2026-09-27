"""Render the beta history and book sizes for Attribution Part 1.

Light/dark and desktop/mobile variants.
"""

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
        "blue": "#76b3d4" if dark else "#32759a",
        # Long, short and net keep Figure 1's colours.
        "long": "#57bdab" if dark else "#268b7b",
        "short": "#e69482" if dark else "#bd6559",
        "net": "#8bb6ee" if dark else "#3a689c",
        "orange": "#e6ae70" if dark else "#ad702c",
        "gray": "#9aa6af" if dark else "#6b7785",
    }
    dates = [dt.date.fromisoformat(value) for value in data["dates"]]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    size = 10 if mobile else 11

    def axis(ax, title, time=True, pad=14):
        ax.set_facecolor(colors["bg"])
        ax.spines[:].set_visible(False)
        ax.grid(axis="y", color=colors["grid"], linewidth=0.5, alpha=0.6)
        ax.set_axisbelow(True)
        ax.set_title(title, loc="left", color=colors["ink"], fontsize=size+1,
                     weight="semibold", pad=pad)
        ax.tick_params(colors=colors["ink"], labelsize=size, length=0, pad=6)
        if time:
            for _, peak, _, end in data["windows"]:
                ax.axvspan(dt.date.fromisoformat(peak), dt.date.fromisoformat(end),
                           color=colors["grid"], alpha=.25, linewidth=0)
            ax.axhline(0, color=colors["grid"], linewidth=.8)
            ax.set_xlim(dates[0], dates[-1])
            ax.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    def save(fig, name):
        fig.set_facecolor(colors["bg"])
        path = OUTPUT / f"{name}{suffix}.svg"
        fig.savefig(path, metadata={"Date": None})
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)

    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "attribution-series"}):
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(4, 6) if mobile else (9.6, 5.8))
        axis(axes[0], "Realized market beta · trailing 252 sessions")
        axis(axes[1], "Standardized beta exposure · per notional")
        axes[0].plot(dates, data["realized_beta"], color=colors["blue"], linewidth=1.25)
        axes[0].margins(y=.08)
        axes[1].plot(dates, data["fit_beta_exposure"], color=colors["blue"], linewidth=1)
        for row in data["lows"]:
            when = dt.date.fromisoformat(row["date"])
            index = data["dates"].index(row["date"])
            for ax, key in zip(axes, ["realized_beta", "fit_beta_exposure"]):
                # A contrasting dot with a background ring stays visible on the line.
                ax.scatter(when, data[key][index], s=42, color=colors["ink"], edgecolor=colors["bg"],
                           linewidth=1.2, zorder=4)
        for ax in axes:
            ax.yaxis.set_major_locator(plt.MaxNLocator(4))
        fig.subplots_adjust(left=.17 if mobile else .085, right=.97, top=.9, bottom=.08, hspace=.4)
        save(fig, "beta-history")

        fig, ax = plt.subplots(figsize=(4, 3.6) if mobile else (9.6, 3.6))
        axis(ax, "Exposure · % of fixed notional")
        for key, label, color, dash, offset in [
            ("long_gross", "Longs", "long", "-", 0),
            ("short_gross", "Shorts", "short", "--", -3),
            ("net_exposure", "Net", "net", "-", 0),
        ]:
            values = np.array(data[key])*100
            ax.plot(dates, values, color=colors[color], linewidth=.9, linestyle=dash)
            ax.annotate(label, (dates[-1], values[-1]), xytext=(7, offset),
                        textcoords="offset points", va="center", fontsize=size, color=colors[color])
        ax.yaxis.set_major_locator(plt.MultipleLocator(50))
        fig.subplots_adjust(left=.14 if mobile else .065, right=.74 if mobile else .88, top=.85, bottom=.16)
        save(fig, "book-sizes")


if __name__ == "__main__":
    history = json.loads((OUTPUT / "beta-history.json").read_text())
    for dark in [False, True]:
        for mobile in [False, True]:
            render(history, dark, mobile)
