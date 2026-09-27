"""Render beta, book sizes (Part 1) and the rebound-control trade-off (Part 3).

Light/dark and desktop/mobile variants. The trade-off reads rally-evaluation.json,
the aggregate output of the attribution project's rally evaluation.
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


def render(data, results, dark, mobile):
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

        # Part 3: each rule's difference from the Original at equal risk, in declines
        # against strong rallies. The dashed line is where extra market beta alone lands.
        fig, ax = plt.subplots(figsize=(4, 4.2) if mobile else (8, 4.4))
        axis(ax, "Strong rallies · points vs Original", time=False)
        ax.grid(axis="x", color=colors["grid"], linewidth=0.5, alpha=0.6)
        ax.axhline(0, color=colors["grid"], linewidth=.8)
        ax.axvline(0, color=colors["grid"], linewidth=.8)
        controls = results["controls"]
        index = results["index_per_unit_beta"]
        reach = 0.045  # extra beta spanned by the reference line
        ax.plot([-reach * index["declines_pp"], reach * index["declines_pp"]],
                [-reach * index["rallies_pp"], reach * index["rallies_pp"]],
                color=colors["gray"], linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.annotate("More market beta", (reach * index["declines_pp"], reach * index["rallies_pp"]),
                    xytext=(5, 0), textcoords="offset points", fontsize=size,
                    color=colors["gray"], ha="left", va="bottom")

        def point(key):
            return controls[key]["declines_pp"], controls[key]["rallies_pp"]

        families = [
            ("Tilt limits", "blue", [f"style_{b}" for b in ("0.30", "0.25", "0.20", "0.15", "0.10")],
             (6, -13), "right"),
            ("Beta limits", "orange", [f"beta_{b}" for b in ("0.50", "0.30", "0.10")],
             (8, 0), "left"),
        ]
        for label, color, keys, offset, align in families:
            xs, ys = zip(*[(0.0, 0.0)] + [point(k) for k in keys])
            ax.plot(xs, ys, color=colors[color], linewidth=1.2, zorder=2)
            ax.scatter(xs[1:], ys[1:], color=colors[color], s=26, zorder=3)
            ax.annotate(f"{label} · ±0.10", (xs[-1], ys[-1]), xytext=offset,
                        textcoords="offset points", ha=align, va="center", fontsize=size,
                        color=colors[color])
        x, y = point("style_0.20")
        ax.annotate("±0.20", (x, y), xytext=(0, 9), textcoords="offset points", ha="center",
                    fontsize=size, color=colors["blue"])
        for key, label, offset in [("vol_5", "Fast scaling", (0, -12)),
                                   ("vol_21", "Slow scaling", (8, 0))]:
            x, y = point(key)
            ax.scatter(x, y, color=colors["gray"], s=26, zorder=3, marker="s")
            ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", fontsize=size,
                        color=colors["gray"], ha="center" if offset[0] == 0 else "left",
                        va="center")
        ax.scatter(0, 0, color=colors["ink"], s=34, marker="D", zorder=4)
        ax.annotate("Original", (0, 0), xytext=(-6, -11), textcoords="offset points",
                    ha="right", fontsize=size, color=colors["ink"])
        ax.set_xlim(-16, 25)
        ax.set_ylim(-4, 16)
        ax.set_xlabel("Market declines · points vs Original", color=colors["ink"], fontsize=size,
                      labelpad=10)
        fig.subplots_adjust(left=.13 if mobile else .08, right=.96, top=.88, bottom=.15)
        save(fig, "control-tradeoff")

if __name__ == "__main__":
    history = json.loads((OUTPUT / "beta-history.json").read_text())
    results = json.loads((OUTPUT / "rally-evaluation.json").read_text())
    for dark in [False, True]:
        for mobile in [False, True]:
            render(history, results, dark, mobile)
