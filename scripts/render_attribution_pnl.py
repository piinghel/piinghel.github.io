"""Attribution P&L through time.

Part 1, Figure 1 (whole-history): cumulative long, short and net P&L above the
net drawdown, with the two deepest drawdowns shaded.

`--outputs` reads the attribution project's daily P&L
(projects/performance_attribution/outputs/full-history-ridge80-b3k155-20260927/daily.parquet) and writes
the aggregate series to assets/portfolio-attribution/pnl-history.json; rendering
reads only that file and the drawdown windows in themes.json. Longs and
shorts are gross, net includes trading costs, all in points of fixed notional.
"""

import argparse
import datetime as dt
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"
# Key, label, line style. Long, short and net keep one colour each across the series.
BOOKS = [("long", "Longs", "-"), ("short", "Shorts", (0, (3.7, 1.6))), ("net", "Net", "-")]


def export(outputs: Path) -> None:
    import polars as pl

    daily = pl.read_parquet(outputs / "daily.parquet").sort("date")
    net = daily["long_pnl"] + daily["short_pnl"] + daily["cost_pnl"]
    if (net - daily["long_short_net"]).abs().max() > 1e-12:
        raise ValueError("long, short and cost P&L do not reconcile to net P&L")

    def points(values):
        return [round(100 * v, 3) for v in values]

    history = {
        "definition": "Cumulative additive P&L in points of fixed notional (longs and shorts "
        "gross, net after trading costs); benchmark is the Russell 1000 price index, "
        "compounded from 100 before the first session.",
        "dates": [d.isoformat() for d in daily["date"]],
        "long": points(daily["long_pnl"].cum_sum()),
        "short": points(daily["short_pnl"].cum_sum()),
        "net": points(net.cum_sum()),
        "benchmark": points((1 + daily["benchmark"]).cum_prod()),
    }
    (OUTPUT / "pnl-history.json").write_text(json.dumps(history, separators=(",", ":")) + "\n")


def palette(dark: bool) -> dict[str, str]:
    return {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4eaf0" if dark else "#263747",
        "grid": "#43505f" if dark else "#d6dfe5",
        "shade": "#1b232d" if dark else "#f1f4f6",
        "long": "#199e70" if dark else "#1baf7a",
        "short": "#d95926" if dark else "#eb6834",
        "net": "#3987e5" if dark else "#2a78d6",
    }


def style_axis(ax, colors, title, size):
    ax.set_facecolor(colors["bg"])
    ax.spines[:].set_visible(False)
    ax.grid(axis="y", color=colors["grid"], linewidth=0.5, alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", color=colors["ink"], fontsize=size + 1, weight="semibold",
                 pad=8)
    ax.tick_params(colors=colors["ink"], labelsize=size, length=0, pad=5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace("-", "−")))


def plot_books(ax, dates, books, colors, size):
    """Cumulative long/short/net lines, each named beside its last value.

    Call after the figure layout and y-limits are final: labels keep one line of
    text apart, and a short leader joins a label that had to move.
    """
    for key, _, dash in BOOKS:
        ax.plot(dates, books[key], color=colors[key], linewidth=1.3, linestyle=dash)
    low, high = ax.get_ylim()
    box = ax.get_position()
    gap = 1.15 * size * (high - low) / (box.height * ax.figure.get_figheight() * 72)
    right = 1 + 6 / (box.width * ax.figure.get_figwidth() * 72)  # six points past the axis
    ends = sorted(((books[key][-1], key, label) for key, label, _ in BOOKS), reverse=True)
    previous = None
    for value, key, label in ends:
        y = value if previous is None else min(value, previous - gap)
        previous = y
        ax.annotate(label, (dates[-1], value), xytext=(right, y),
                    textcoords=("axes fraction", "data"), va="center", ha="left",
                    fontsize=size, color=colors[key], annotation_clip=False,
                    arrowprops={"arrowstyle": "-", "color": colors[key], "linewidth": 0.7,
                                "shrinkA": 1, "shrinkB": 2})


def save(fig, name, colors, dark, mobile):
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    path = OUTPUT / f"{name}{suffix}.svg"
    fig.savefig(path, metadata={"Date": None}, facecolor=colors["bg"])
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def render_whole_history(history, windows, dark, mobile):
    colors = palette(dark)
    size = 11
    dates = [dt.date.fromisoformat(d) for d in history["dates"]]
    net = np.array(history["net"])
    drawdown = net - np.maximum.accumulate(np.maximum(net, 0))
    fig, (top, bottom) = plt.subplots(
        2, 1, sharex=True, figsize=(4.0, 5.6) if mobile else (8.8, 6.4),
        gridspec_kw={"height_ratios": [1.7, 1], "hspace": 0.32},
    )
    style_axis(top, colors, "Cumulative P&L (points)", size)
    style_axis(bottom, colors, "Drawdown (points)", size)
    for ax in (top, bottom):
        for peak, end in windows:
            ax.axvspan(dt.date.fromisoformat(peak), dt.date.fromisoformat(end),
                       color=colors["shade"], linewidth=0, zorder=0)
    top.axhline(0, color=colors["grid"], linewidth=0.9)
    bottom.axhline(0, color=colors["ink"], linewidth=0.6)
    bottom.plot(dates, drawdown, color=colors["net"], linewidth=1.0)
    top.set_ylim(-125, 475)
    top.yaxis.set_major_locator(plt.MultipleLocator(100))
    bottom.yaxis.set_major_locator(plt.MultipleLocator(5))
    bottom.set_xlim(dates[0], dates[-1])
    bottom.xaxis.set_major_locator(mdates.YearLocator(8 if mobile else 4, month=1, day=1))
    bottom.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.subplots_adjust(left=0.13 if mobile else 0.07, right=0.8 if mobile else 0.88,
                        top=0.94, bottom=0.06 if mobile else 0.05)
    plot_books(top, dates, history, colors, size)
    save(fig, "whole-history", colors, dark, mobile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, help="attribution full_history output folder")
    args = parser.parse_args()
    if args.outputs:
        export(args.outputs)
    history = json.loads((OUTPUT / "pnl-history.json").read_text())
    windows = json.loads((OUTPUT / "themes.json").read_text())["windows"]
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "attribution-pnl",
                         # Drop vertices that move a daily path by under a quarter point.
                         "path.simplify_threshold": 0.25}):
        for dark in (False, True):
            for mobile in (False, True):
                render_whole_history(history, windows, dark, mobile)
