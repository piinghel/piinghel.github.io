"""Render the unpublished attribution study from its verified saved observations."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def prepare_axis(ax, colors):
    ax.set_facecolor(colors["background"])
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0, colors=colors["text"], labelsize=11)
    ax.set_axisbelow(True)


def pnl_bridge(data, colors, mobile):
    values = [data[key] for key in ("long_pnl", "short_pnl", "cost_pnl", "net")]
    if abs(sum(values[:3]) - values[3]) > 1e-10:
        raise ValueError("Book components do not reconcile")
    fig, ax = plt.subplots(figsize=(5.0 if mobile else 8.8, 4.5))
    prepare_axis(ax, colors)
    running = 0.0
    for i, value in enumerate(values):
        start = running if i < 3 else 0.0
        end = start + value
        color = colors["positive"] if value >= 0 else colors["negative"]
        if i == 3:
            color = colors["accent"]
        ax.bar(i, end - start, bottom=start, width=0.60, color=color, zorder=3)
        ax.annotate(f"{value:+.3f}", (i, max(start, end)), xytext=(0, 8),
                    textcoords="offset points", ha="center", fontsize=11,
                    weight="bold", color=colors["text"])
        if i < 2:
            ax.plot([i + .30, i + .70], [end, end], color=colors["grid"], lw=1)
        running = end
    ax.axhline(0, color=colors["text"], lw=.7)
    ax.set_xticks(range(4), ["Longs", "Shorts", "Costs", "Net"])
    ax.set_yticks([-10, -5, 0, 5, 10])
    ax.set_ylim(-11, 11)
    ax.set_xlim(-.55, 3.55)
    ax.grid(axis="y", color=colors["grid"], lw=.6)
    ax.set_ylabel("P&L / fixed notional (pp)", color=colors["text"], fontsize=11)
    fig.subplots_adjust(left=.15 if mobile else .10, right=.99, top=.95, bottom=.12)
    return fig


def prediction_endpoints(stock, colors, mobile):
    first = sum(row["contribution_first"] for row in stock["top_five"])
    last = sum(row["contribution_last"] for row in stock["top_five"])
    scores = stock["scores"]
    starts = [first, scores["score_first"] - first, scores["score_first"]]
    ends = [last, scores["score_last"] - last, scores["score_last"]]
    fig, ax = plt.subplots(figsize=(5.0 if mobile else 8.8, 5.2 if mobile else 4.4))
    prepare_axis(ax, colors)
    for i, (start, end) in enumerate(zip(starts, ends)):
        y = 2 - i
        ax.plot([start, end], [y, y], color=colors["grid"], lw=2)
        ax.scatter(start, y, s=64, facecolor=colors["background"],
                   edgecolor=colors["accent"], lw=1.7, zorder=3,
                   label="29 Dec 2022" if i == 0 else None)
        ax.scatter(end, y, s=58, color=colors["accent"], marker="D", zorder=3,
                   label="2 Feb 2023" if i == 0 else None)
        for value, offset in [(start, 13), (end, -23)]:
            ax.annotate(f"{value:+.4f}", (value, y), xytext=(0, offset),
                        textcoords="offset points", ha="center", fontsize=11,
                        color=colors["text"])
    ax.set_yticks([2, 1, 0], ["Five displayed\npredictors", "Remaining terms\n+ intercept", "Full prediction"])
    ax.set_ylim(-.7, 2.65)
    ax.set_xlim(-.132, .048)
    ax.set_xticks([-.12, -.08, -.04, 0, .04])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.2f}"))
    ax.axvline(0, color=colors["text"], lw=.7)
    ax.grid(axis="x", color=colors["grid"], lw=.5)
    ax.set_xlabel("Model-score units", color=colors["text"], fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, 1.13), ncol=2,
              frameon=False, labelcolor=colors["text"], fontsize=10)
    fig.subplots_adjust(left=.30 if mobile else .22, right=.97, top=.85, bottom=.14)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.read_bytes()
    if hashlib.sha256(source).hexdigest() != args.source_sha256:
        raise ValueError("Source differs from the verified registry artifact")
    data = json.loads(source)
    # Only aggregate values and model-score endpoints enter the SVGs.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for dark in [False, True]:
        colors = {
            "background": "#171d24" if dark else "#ffffff",
            "text": "#e4eaf0" if dark else "#263747",
            "grid": "#43505f" if dark else "#d6dfe5",
            "positive": "#57bdab" if dark else "#268b7b",
            "negative": "#e69482" if dark else "#bd6559",
            "accent": "#8bb6ee" if dark else "#3a689c",
        }
        with plt.rc_context({"font.family": "Arial", "svg.fonttype": "none",
                             "svg.hashsalt": "attribution-study"}):
            for mobile in [False, True]:
                suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
                for name, renderer, observations in [
                    ("episode-bridge", pnl_bridge, data["episode"]),
                    ("rocket-prediction", prediction_endpoints, data["Rocket"]),
                ]:
                    fig = renderer(observations, colors, mobile)
                    fig.savefig(args.output_dir / f"{name}{suffix}.svg",
                                facecolor=colors["background"], metadata={"Date": None})
                    plt.close(fig)


if __name__ == "__main__":
    main()
