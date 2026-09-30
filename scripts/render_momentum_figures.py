"""Static figure for the momentum-crash article: Ridge-80 Sharpe by rule (development period).

Values are the verified schedule means and lowest/highest schedule Sharpe ratios
(data/momentum_crash_layers_review_20260930/out/ridge_stats.csv, review_ridge_stats.csv).
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

# label, mean, low, high, family
ROWS = [
    ("Baseline", 1.317, 1.256, 1.358, "base"),
    ("Constant shrink (no timing)", 1.409, 1.339, 1.450, "control"),
    ("Optimizer cap 0.45/g", 1.449, 1.388, 1.495, "cap"),
    ("Optimizer cap 0.45/g²", 1.469, 1.411, 1.525, "cap"),
    ("Score overlay", 1.541, 1.441, 1.612, "overlay"),
    ("Learned interactions", 1.547, 1.481, 1.613, "learned"),
    ("Learned + cap", 1.596, 1.551, 1.658, "combo"),
    ("Learned + overlay", 1.666, 1.570, 1.743, "combo"),
]
MARKER = {"base": "o", "control": "o", "cap": "s", "overlay": "^", "learned": "D", "combo": "*"}


def palette(dark: bool) -> dict[str, str]:
    return {"bg": "#0d1117" if dark else "#ffffff", "ink": "#e4e7ea" if dark else "#25313a",
            "muted": "#9ba5af" if dark else "#59636e", "grid": "#37414a" if dark else "#e2e6e9",
            "base": "#6e7681" if dark else "#a3acb5", "control": "#8b949e" if dark else "#6e7781",
            "cap": "#2aa3c4" if dark else "#0e8fad", "overlay": "#3987e5" if dark else "#2a78d6",
            "learned": "#a8891a" if dark else "#b58900", "combo": "#9085e9" if dark else "#7447c9"}


def render(out: Path, dark: bool, mobile: bool) -> None:
    c = palette(dark)
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"],
                         "svg.fonttype": "none", "svg.hashsalt": "momentum-sharpe"}):
        fig, ax = plt.subplots(figsize=(3.9, 4.4) if mobile else (7.6, 3.9))
        fig.set_facecolor(c["bg"]); ax.set_facecolor(c["bg"])
        ys = list(range(len(ROWS)))[::-1]
        ax.axvline(ROWS[0][1], color=c["muted"], lw=0.8, ls=(0, (2, 3)), zorder=1)
        for y, (label, m, lo, hi, fam) in zip(ys, ROWS):
            ax.plot([lo, hi], [y, y], color=c[fam], lw=2.0, solid_capstyle="butt", zorder=2)
            size = 11 if fam == "combo" else 7.5
            face = c["bg"] if fam == "control" else c[fam]
            ax.plot(m, y, MARKER[fam], ms=size, mfc=face, mec=c[fam], mew=1.4, zorder=3)
        ax.set_yticks(ys, [r[0] for r in ROWS])
        for tick, row in zip(ax.get_yticklabels(), ROWS):
            tick.set_color(c["ink"]); tick.set_fontweight("bold" if row[0] == "Score overlay" else "normal")
        ax.set_xlim(1.2, 1.8); ax.set_xticks([1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])
        ax.tick_params(axis="x", colors=c["muted"], labelsize=10 if mobile else 10.5, length=0)
        ax.tick_params(axis="y", length=0, labelsize=10 if mobile else 11, pad=6)
        ax.grid(axis="x", color=c["grid"], lw=0.8); ax.set_axisbelow(True)
        for side in ax.spines.values(): side.set_visible(False)
        ax.set_title("Net Sharpe ratio", loc="left", fontsize=11 if mobile else 11.5, color=c["ink"], pad=10,
                     x=-0.72 if mobile else -0.36)
        fig.tight_layout()
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        fig.savefig(out / f"sharpe-by-rule{suffix}.svg", metadata={"Date": None}, facecolor=c["bg"])
        plt.close(fig)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "assets/momentum-crashes"
    out.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        for mobile in (False, True):
            render(out, dark, mobile)
