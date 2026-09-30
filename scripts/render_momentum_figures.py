"""Static figure for the momentum-crash article: Ridge-80 Sharpe and maximum drawdown by rule (development period).

Values are the verified schedule means and lowest/highest schedule Sharpe ratios
(data/momentum_crash_layers_review_20260930/out/ridge_stats.csv, review_ridge_stats.csv).
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

# label, Sharpe mean/low/high, compounded max drawdown % mean/low/high (per schedule), family
ROWS = [
    ("Baseline", 1.317, 1.256, 1.358, 15.5, 14.9, 16.0, "base"),
    ("Constant shrink (no timing)", 1.409, 1.339, 1.450, 13.4, 12.6, 14.5, "control"),
    ("Optimizer cap 0.45/g", 1.449, 1.388, 1.495, 11.9, 10.9, 12.6, "cap"),
    ("Optimizer cap 0.45/g²", 1.469, 1.411, 1.525, 11.4, 10.6, 12.2, "cap"),
    ("Score overlay", 1.541, 1.441, 1.612, 11.9, 10.8, 12.6, "overlay"),
    ("Learned interactions", 1.547, 1.481, 1.613, 13.3, 12.0, 14.7, "learned"),
    ("Learned + cap", 1.596, 1.551, 1.658, 13.1, 12.0, 14.1, "combo"),
    ("Learned + overlay", 1.666, 1.570, 1.743, 13.5, 11.6, 15.9, "combo"),
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
        if mobile:
            fig, axes = plt.subplots(2, 1, figsize=(3.9, 8.4), gridspec_kw={"hspace": 0.38})
        else:
            fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.1), sharey=True, gridspec_kw={"wspace": 0.12, "width_ratios": [1.2, 1]})
        fig.set_facecolor(c["bg"])
        ys = list(range(len(ROWS)))[::-1]
        # Drawdowns are plotted as negative numbers so that right means better in both panels.
        panels = [("Net Sharpe ratio", lambda r: (r[1], r[2], r[3]), (1.2, 1.8), [1.2, 1.4, 1.6, 1.8] if mobile else [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]),
                  ("Maximum drawdown (%)", lambda r: (-r[4], -r[6], -r[5]), (-17, -9), [-16, -14, -12, -10])]
        for k, (ax, (title, get, lim, ticks)) in enumerate(zip(axes, panels)):
            ax.set_facecolor(c["bg"])
            base = get(ROWS[0])[0]
            ax.axvline(base, color=c["muted"], lw=0.8, ls=(0, (2, 3)), zorder=1)
            for y, row in zip(ys, ROWS):
                fam = row[-1]; m, lo, hi = get(row)
                ax.plot([lo, hi], [y, y], color=c[fam], lw=2.0, solid_capstyle="butt", zorder=2)
                size = 11 if fam == "combo" else 7.5
                ax.plot(m, y, MARKER[fam], ms=size, mfc=c["bg"] if fam == "control" else c[fam], mec=c[fam], mew=1.4, zorder=3)
            ax.set_xlim(*lim); ax.set_xticks(ticks)
            if k == 1:
                ax.set_xticklabels([f"{abs(t)}" if t else "0" for t in ticks])
            ax.tick_params(axis="x", colors=c["muted"], labelsize=10 if mobile else 10.5, length=0)
            ax.tick_params(axis="y", length=0, labelsize=10 if mobile else 11, pad=6)
            ax.grid(axis="x", color=c["grid"], lw=0.8); ax.set_axisbelow(True)
            for side in ax.spines.values(): side.set_visible(False)
            ax.set_title(title, loc="left", fontsize=11 if mobile else 11.5, color=c["ink"], pad=10)
            if k == 0 or mobile:
                ax.set_yticks(ys, [r[0] for r in ROWS])
                for tick, row in zip(ax.get_yticklabels(), ROWS):
                    tick.set_color(c["ink"]); tick.set_fontweight("bold" if row[0] == "Score overlay" else "normal")
            else:
                ax.tick_params(axis="y", labelleft=False)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = out / f"sharpe-by-rule{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=c["bg"], bbox_inches="tight", pad_inches=0.12)
        plt.close(fig)
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "assets/momentum-crashes"
    out.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        for mobile in (False, True):
            render(out, dark, mobile)
