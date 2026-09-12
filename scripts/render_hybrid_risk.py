"""Render the hybrid risk article from retained aggregate comparison results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render(rows: list[dict], output: Path, *, dark: bool, mobile: bool) -> None:
    """Show calibration and allocation as separate questions, with stable row order."""
    colors = dict(bg="#0b1117" if dark else "#ffffff", ink="#c6cdd5" if dark else "#263747",
                  grid="#39434e" if dark else "#d9e0e7", point="#88b4de" if dark else "#356b9a")
    labels = ["Incumbent", "Incumbent, adaptive", "Hybrid", "50:50 covariance blend"]
    if mobile:
        labels = ["Incumbent", "Incumbent,\nadaptive", "Hybrid", "50:50 covariance\nblend"]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "hybrid-risk"}):
        for name in ["calibration", "portfolio-tradeoff"]:
            calibration = name == "calibration"
            fig, axes = plt.subplots(1, 1 if calibration else 2, squeeze=False,
                                     figsize=(4.5, 3.3) if mobile else (9.75, 3.5))
            fig.patch.set_facecolor(colors["bg"])
            for j, ax in enumerate(axes[0]):
                ax.set_facecolor(colors["bg"])
                ax.spines[:].set_visible(False)
                ax.set_ylim(3.6, -.65)
                ax.set_yticks(range(4), labels if j == 0 else [])
                ax.tick_params(length=0, colors=colors["ink"], labelsize=11 if mobile else 12, pad=6)
                ax.grid(axis="x", color=colors["grid"], lw=.55)
                ax.set_axisbelow(True)
                if calibration:
                    key, limits, ticks, title = "mean_volatility_ratio", (.98, 1.16), [1., 1.05, 1.10, 1.15], "Realized / forecast volatility"
                    ax.axvline(1, color=colors["ink"], lw=.9)
                elif j == 0:
                    key, limits, ticks, title = "annual_net_pct", (9, 13), [9, 11, 13], "Net return (%)"
                else:
                    key, limits, ticks, title = "max_drawdown_pct", (-21, -14), [-20, -17, -14], "Drawdown (pp)"
                ax.set_xlim(*limits)
                ax.set_xticks(ticks)
                ax.set_title(title, loc="left", fontsize=11.5 if mobile else 14, fontweight="bold",
                             color=colors["ink"], pad=14)
                for y, row in enumerate(rows):
                    value = row[key]
                    assert limits[0] < value < limits[1], (key, value)
                    ax.plot(value, y, "o", ms=6, color=colors["point"])
            fig.subplots_adjust(left=.38 if mobile else .30, right=.96, bottom=.15, top=.80,
                                wspace=.40 if mobile else .25)
            target = output / f"{name}{suffix}.svg"
            fig.savefig(target, metadata={"Date": None})
            target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
            plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/hybrid-risk-model")
    args = parser.parse_args()
    rows = json.loads((args.assets / "metrics.json").read_text())["rows"]
    if [r["arm"] for r in rows] != ["baseline_fixed", "baseline", "B", "C"]:
        raise ValueError("Unexpected model order")
    for dark in [False, True]:
        for mobile in [False, True]:
            render(rows, args.assets, dark=dark, mobile=mobile)


if __name__ == "__main__":
    main()
