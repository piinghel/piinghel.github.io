"""Generate the selected Ridge portfolio-exposure time series."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_data" / "multiple_linear_regression_selected_exposure.csv"
OUTPUT_DIR = ROOT / "assets" / "multiple-linear-regression"

INK = "#33404b"
MUTED = "#66737e"
GRID = "#dbe1e3"
WHITE = "#ffffff"
TEAL = "#477c80"
CORAL = "#a96760"
GOLD = "#a78243"


def prepare_source(raw_output: Path) -> None:
    """Compact the three execution calendars to monthly portfolio exposures."""
    calendar_files = sorted(
        (raw_output / "backtest" / "calendars").glob("*/floating_weights.csv")
    )
    if len(calendar_files) != 3:
        raise ValueError(
            f"expected three floating-weight files below {raw_output}, "
            f"found {len(calendar_files)}"
        )

    daily: dict[date, list[tuple[float, float]]] = defaultdict(list)
    for path in calendar_files:
        with path.open(encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                daily[date.fromisoformat(row["date"])].append(
                    (
                        float(row["floating_weight_long"]),
                        float(row["floating_weight_short"]),
                    )
                )

    combined: list[tuple[date, float, float, float]] = []
    for current_date, values in sorted(daily.items()):
        long_gross = sum(value[0] for value in values) / len(values)
        short_gross = sum(value[1] for value in values) / len(values)
        combined.append(
            (current_date, long_gross, short_gross, long_gross - short_gross)
        )

    expected = {
        "development": (
            date(1998, 9, 29),
            date(2021, 12, 31),
            0.8481309316,
            0.5481803842,
        ),
        "later": (
            date(2022, 1, 3),
            date(2026, 5, 27),
            0.9020377732,
            0.4334423034,
        ),
    }
    for label, (start, end, expected_long, expected_short) in expected.items():
        rows = [row for row in combined if start <= row[0] <= end]
        observed_long = sum(row[1] for row in rows) / len(rows)
        observed_short = sum(row[2] for row in rows) / len(rows)
        if abs(observed_long - expected_long) > 5e-7 or abs(observed_short - expected_short) > 5e-7:
            raise ValueError(
                f"{label} exposure mismatch: "
                f"long={observed_long:.10f}, short={observed_short:.10f}"
            )

    monthly: dict[tuple[int, int], list[tuple[date, float, float, float]]] = defaultdict(list)
    for row in combined:
        monthly[(row[0].year, row[0].month)].append(row)

    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(("date", "long_gross", "short_gross", "net_stock_exposure"))
        for rows in monthly.values():
            writer.writerow(
                (
                    rows[-1][0].isoformat(),
                    f"{sum(row[1] for row in rows) / len(rows):.10f}",
                    f"{sum(row[2] for row in rows) / len(rows):.10f}",
                    f"{sum(row[3] for row in rows) / len(rows):.10f}",
                )
            )


def load_source() -> tuple[list[date], list[float], list[float], list[float]]:
    dates: list[date] = []
    long_gross: list[float] = []
    short_gross: list[float] = []
    net: list[float] = []
    with SOURCE.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            dates.append(date.fromisoformat(row["date"]))
            long_gross.append(float(row["long_gross"]))
            short_gross.append(float(row["short_gross"]))
            net.append(float(row["net_stock_exposure"]))
    if not dates:
        raise ValueError(f"no exposure rows in {SOURCE}")
    return dates, long_gross, short_gross, net


def draw(*, mobile: bool) -> None:
    dates, long_gross, short_gross, net = load_source()
    figsize = (5.2, 4.2) if mobile else (9.0, 4.4)
    fig, ax = plt.subplots(figsize=figsize, facecolor=WHITE)
    fig.subplots_adjust(
        left=0.16 if mobile else 0.105,
        right=0.98,
        top=0.82,
        bottom=0.18,
    )

    ax.plot(dates, long_gross, color=TEAL, linewidth=1.8, label="Long gross")
    ax.plot(dates, short_gross, color=CORAL, linewidth=1.8, label="Short gross")
    ax.plot(dates, net, color=GOLD, linewidth=1.8, label="Net stock exposure")
    boundary = date(2022, 1, 1)
    ax.axvline(boundary, color=MUTED, linewidth=1.0, linestyle=(0, (3, 3)))
    ax.text(
        boundary,
        1.015,
        "2022",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="bottom",
        color=MUTED,
        fontsize=9.0,
    )

    lower = min(0.0, min(net) - 0.03)
    upper = min(1.05, max(long_gross) + 0.05)
    ax.set_ylim(lower, upper)
    ax.set_xlim(dates[0], dates[-1])
    ax.margins(x=0)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.xaxis.set_major_locator(mdates.YearLocator(5 if mobile else 4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylabel("Portfolio weight", color=INK, fontsize=10.5)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, colors=MUTED, labelsize=9.2)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0.0, 1.08),
        ncol=1 if mobile else 3,
        frameon=False,
        borderaxespad=0,
        handlelength=2.4,
        columnspacing=1.8,
        labelcolor=INK,
        fontsize=9.5,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "-mobile" if mobile else ""
    svg_path = OUTPUT_DIR / f"portfolio-exposures{suffix}.svg"
    png_path = OUTPUT_DIR / f"portfolio-exposures{suffix}.png"
    fig.savefig(svg_path, format="svg", facecolor=WHITE)
    svg_path.write_text(
        "\n".join(
            line.rstrip()
            for line in svg_path.read_text(encoding="utf-8").splitlines()
        )
        + "\n",
        encoding="utf-8",
    )
    fig.savefig(png_path, dpi=240, facecolor=WHITE)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-output",
        type=Path,
        help="Optional locked Ridge output used to refresh the compact source.",
    )
    args = parser.parse_args()
    if args.raw_output is not None:
        prepare_source(args.raw_output)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": WHITE,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
        }
    )
    draw(mobile=False)
    draw(mobile=True)


if __name__ == "__main__":
    main()
