"""Render beta, book sizes and the cap trade-off in light/dark, desktop/mobile."""

import datetime as dt
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"


def render(data, results, dark, mobile):
    colors = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4eaf0" if dark else "#263747",
        "grid": "#43505f" if dark else "#d6dfe5",
        "blue": "#76b3d4" if dark else "#32759a",
        "orange": "#e6ae70" if dark else "#ad702c",
        "green": "#88bca5" if dark else "#397c61",
    }
    dates = [dt.date.fromisoformat(value) for value in data["dates"]]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    size = 10 if mobile else 11

    def axis(ax, title, time=True):
        ax.set_facecolor(colors["bg"])
        ax.spines[:].set_visible(False)
        ax.grid(axis="y", color=colors["grid"], linewidth=0.5, alpha=0.6)
        ax.set_axisbelow(True)
        ax.set_title(title, loc="left", color=colors["ink"], fontsize=size+1,
                     weight="semibold", pad=14)
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
        axis(axes[0], "Realized market beta")
        axis(axes[1], "Model beta exposure · per notional")
        for key, color, label, width in [("beta_126", "orange", "126 sessions", .85),
                                         ("realized_beta", "blue", "252 sessions", 1.25)]:
            axes[0].plot(dates, data[key], color=colors[color], linewidth=width, label=label)
        axes[0].legend(loc="upper left", bbox_to_anchor=(0, 1.02), ncol=2, frameon=False,
                       fontsize=9 if mobile else 10, labelcolor=colors["ink"], borderaxespad=0,
                       handlelength=1.5, columnspacing=1)
        axes[0].margins(y=.22)
        axes[1].plot(dates, data["model_beta"], color=colors["blue"], linewidth=1)
        for row in data["lows"]:
            when = dt.date.fromisoformat(row["date"])
            for ax, key in zip(axes, ["realized_beta", "model_beta"]):
                ax.scatter(when, row[key], s=20, color=colors["blue"], zorder=4)
            axes[1].annotate(row["date"][:4], (when, row["model_beta"]), xytext=(0, -18),
                             textcoords="offset points", ha="center", fontsize=9, color=colors["ink"])
        for ax in axes:
            ax.yaxis.set_major_locator(plt.MaxNLocator(4))
        fig.subplots_adjust(left=.17 if mobile else .085, right=.97, top=.90, bottom=.08, hspace=.57)
        save(fig, "beta-history")

        fig, ax = plt.subplots(figsize=(4, 3.6) if mobile else (9.6, 3.6))
        axis(ax, "Exposure · % of fixed notional")
        for key, label, color, dash, offset in [
            ("long_gross", "Long gross", "blue", "-", 0),
            ("short_gross", "Short gross", "orange", "--", -3),
            ("net_exposure", "Net", "green", "-", 0),
        ]:
            values = np.array(data[key])*100
            ax.plot(dates, values, color=colors[color], linewidth=.9, linestyle=dash)
            ax.annotate(label, (dates[-1], values[-1]), xytext=(7, offset),
                        textcoords="offset points", va="center", fontsize=size, color=colors[color])
        ax.yaxis.set_major_locator(plt.MultipleLocator(50))
        fig.subplots_adjust(left=.14 if mobile else .065, right=.74 if mobile else .88, top=.85, bottom=.16)
        save(fig, "book-sizes")

        fig, ax = plt.subplots(figsize=(4, 3.9) if mobile else (8, 4))
        axis(ax, "Worst drawdown · P&L points", time=False)
        rows = [row for row in results["original_summaries"]
                if row["variant"] == "baseline" or row["variant"].startswith("style_")]
        rows.sort(key=lambda row: row["annual_net_pp"])
        ax.plot([r["annual_net_pp"] for r in rows], [r["max_drawdown_pp"] for r in rows],
                color=colors["grid"], linewidth=1, zorder=1)
        offsets = {"0.30": (8, 4), "0.25": (-8, -15)}
        for row in rows:
            original = row["variant"] == "baseline"
            label = "Original" if original else "±"+row["variant"].split("_")[1]
            x, y = row["annual_net_pp"], row["max_drawdown_pp"]
            color = colors["ink"] if original else colors["blue"]
            ax.scatter(x, y, color=color, s=34, zorder=3, marker="D" if original else "o")
            offset = (-8, 6) if original else offsets.get(label[1:], (0, 9))
            ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", fontsize=size,
                        color=color, ha="right" if offset[0]<0 else "left" if offset[0]>0 else "center")
        ax.set_xlim(9.45, 11.65)
        ax.set_ylim(-17, -10.7)
        ax.set_yticks([-16, -14, -12])
        ax.set_xticks([9.5, 10, 10.5, 11, 11.5])
        ax.set_xlabel("Net P&L per year · points", color=colors["ink"], fontsize=size, labelpad=12)
        fig.subplots_adjust(left=.16 if mobile else .1, right=.97, top=.85, bottom=.2)
        save(fig, "cap-tradeoff")


if __name__ == "__main__":
    history = json.loads((OUTPUT / "beta-history.json").read_text())
    results = json.loads((OUTPUT / "series-diagnostics.json").read_text())
    for dark in [False, True]:
        for mobile in [False, True]:
            render(history, results, dark, mobile)
