"""Regression article, Figure 2: the twelve expanding walk-forward refits on a real
time axis, with the test period shaded. Windows come from the evidence file
chosen_penalty_by_refit.csv (training end and prediction start of each refit);
every training window starts on the first panel date."""

import csv
import datetime as dt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "combining-predictors"
WINDOWS = OUT / "evidence/results/chosen_penalty_by_refit.csv"
TRAIN_START = dt.date(1995, 1, 12)
LAST_DATE = dt.date(2026, 5, 27)
TEST_START = dt.date(2022, 1, 3)


def windows() -> list[tuple[dt.date, dt.date, dt.date]]:
    """(training end, prediction start, prediction end) for each refit."""
    rows = list(csv.DictReader(WINDOWS.open()))
    starts = [dt.date.fromisoformat(r["test_start"]) for r in rows]
    ends = [s - dt.timedelta(days=1) for s in starts[1:]] + [LAST_DATE]
    return [
        (dt.date.fromisoformat(r["validation_end"]), start, end)
        for r, start, end in zip(rows, starts, ends, strict=True)
    ]


def render(*, dark: bool, mobile: bool) -> None:
    c = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4e7ea" if dark else "#25313a",
        "muted": "#9aa6af" if dark else "#5d6b76",
        "train": "#2c4a63" if dark else "#d6e4f0",
        "predict": "#3987e5" if dark else "#2a78d6",
        "test": "#1b222b" if dark else "#f1f3f5",
    }
    # Point sizes that render at roughly 12-13 CSS px at each viewport's display width.
    label, tick = (12, 11.5) if mobile else (10.5, 10)
    refits = windows()
    num = mdates.date2num
    with plt.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "svg.hashsalt": "mlr-walk-forward",
        }
    ):
        fig, ax = plt.subplots(figsize=(4.8, 4.9) if mobile else (8.4, 4.0))
        fig.set_facecolor(c["bg"])
        ax.set_facecolor(c["bg"])
        ax.axvspan(num(TEST_START), num(LAST_DATE), color=c["test"], zorder=0, linewidth=0)
        for row, (train_end, start, end) in enumerate(refits):
            ax.barh(row, num(train_end) - num(TRAIN_START), left=num(TRAIN_START),
                    height=0.56, color=c["train"], zorder=2)
            # A thin background edge separates each prediction block from its training window.
            ax.barh(row, num(end) - num(start), left=num(start), height=0.56,
                    color=c["predict"], edgecolor=c["bg"], linewidth=1.2, zorder=2)
        for x, text in ((TRAIN_START + (TEST_START - TRAIN_START) / 2, "Development"),
                        (TEST_START + (LAST_DATE - TEST_START) / 2, "Later")):
            ax.annotate(text, (num(x), -0.9), ha="center", va="bottom", fontsize=label - 0.5,
                        color=c["muted"], annotation_clip=False)
        # A compact key: every green block is out of sample, in both periods.
        ax.legend(
            handles=[Patch(color=c["train"], label="Training window"),
                     Patch(color=c["predict"], label="Out-of-sample predictions")],
            loc="lower left", bbox_to_anchor=(0, 1.05), ncol=1 if mobile else 2,
            frameon=False, fontsize=label, labelcolor=c["ink"], borderaxespad=0,
            handlelength=1.0, handleheight=0.9, handletextpad=0.5, columnspacing=1.6,
        )
        ax.set_yticks([])
        ax.set_ylim(len(refits) - 0.45, -1.45)
        ax.set_xlim(num(dt.date(1994, 10, 1)), num(LAST_DATE))
        ax.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0, colors=c["muted"], labelsize=tick)
        fig.subplots_adjust(left=0.03, right=0.97, top=0.81 if mobile else 0.86,
                            bottom=0.08 if mobile else 0.09)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUT / f"expanding-walk-forward{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=c["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    for mobile in (False, True):
        for dark in (False, True):
            render(dark=dark, mobile=mobile)
