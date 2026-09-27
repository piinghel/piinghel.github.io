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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "multiple-linear-regression"
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
        "predict": "#6eb5a5" if dark else "#378579",
        "test": "#1b222b" if dark else "#f1f3f5",
    }
    size = 10.5 if mobile else 11
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
        fig, ax = plt.subplots(figsize=(4.8, 4.8) if mobile else (8.4, 4.0))
        fig.set_facecolor(c["bg"])
        ax.set_facecolor(c["bg"])
        ax.axvspan(num(TEST_START), num(LAST_DATE), color=c["test"], zorder=0, linewidth=0)
        for row, (train_end, start, end) in enumerate(refits):
            ax.barh(row, num(train_end) - num(TRAIN_START), left=num(TRAIN_START),
                    height=0.62, color=c["train"], zorder=2)
            ax.barh(row, num(end) - num(start), left=num(start),
                    height=0.62, color=c["predict"], zorder=2)
        _, _, first_end = refits[0]
        ax.annotate("Training", (num(TRAIN_START), len(refits) - 1), xytext=(5, 0),
                    textcoords="offset points", va="center", ha="left", fontsize=size - 1.5,
                    color=c["ink"], zorder=3)
        ax.annotate("Predictions", (num(first_end), 0), xytext=(5, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=size - 1.5, color=c["predict"], zorder=3)
        for x, label in ((dt.date(2008, 1, 1), "Development"),
                         (TEST_START + (LAST_DATE - TEST_START) / 2, "Test")):
            ax.annotate(label, (num(x), -1.0), ha="center", va="bottom", fontsize=size - 1,
                        color=c["muted"], annotation_clip=False)
        ax.set_yticks(range(len(refits)), [str(start.year) for _, start, _ in refits])
        ax.set_ylim(len(refits) - 0.4, -1.2)
        ax.set_xlim(num(dt.date(1994, 7, 1)), num(dt.date(2026, 12, 31)))
        ax.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0, colors=c["muted"], labelsize=size - 1)
        fig.subplots_adjust(left=0.13 if mobile else 0.07, right=0.98, top=0.93, bottom=0.08)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUT / f"expanding-walk-forward{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=c["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    for mobile in (False, True):
        for dark in (False, True):
            render(dark=dark, mobile=mobile)
