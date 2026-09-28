"""Export the attribution series' public aggregates from a theme-attribution output folder.

Reads ``theme_months.parquet`` written by the performance_attribution theme study
(studies/2026-09-theme-attribution-over-time/tables.py) and writes
``assets/portfolio-attribution/attribution-months.json`` for the period explorer:
per month and leg, each theme's summed daily P&L and summed P&L x book return, plus the
book's sessions, sum and sum of squares. A window's return is 252 x sum / sessions and
its share of risk is (sum_x - sum x book_sum / n) / (book_sum2 - book_sum^2 / n).

    python scripts/export_attribution_series.py \
        --outputs ../../projects/performance_attribution/outputs/<attribution folder>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import polars as pl

ASSETS = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"
LEGS = ("total", "long", "short")
# Display grouping of the explorer: signal themes, the low-beta package, the rest.
# Every name must be a line in theme_months.parquet; the package row is its subtotal.
GROUPS = [
    {"label": "Signals", "lines": ["Short interest", "Short-term return", "Long-term return", "Size"]},
    {"label": "Trading activity", "total": "Trading activity",
     "lines": ["Turnover", "Volume surge", "Price-volume correlation"]},
    {"label": "Low-risk package", "total": "Low-risk package",
     "lines": ["Low volatility", "Beta", "Net market exposure"]},
    {"label": "Other", "lines": ["Sector tilt", "Stock-specific", "Unloaded holdings", "Trading costs"]},
]


def export(outputs: Path, destination: Path, *, legs: tuple[str, ...] = LEGS,
           groups: list[dict] = GROUPS) -> dict:
    """Collect the monthly sums into a compact, column-oriented JSON document."""
    frame = pl.read_parquet(outputs / "theme_months.parquet")
    months = sorted(frame["month"].unique().to_list())
    book = frame.filter(pl.col("line") == "Book").sort("month")
    if book["month"].to_list() != months:
        raise ValueError("book sums must cover every month")
    wanted = {n for g in groups for n in [*g["lines"], g.get("total")] if n}
    missing = wanted - set(frame["line"])
    if missing:
        raise KeyError(f"display lines missing from the output: {sorted(missing)}")

    def series(sub: pl.DataFrame, column: str, scale: float) -> list[float]:
        values = dict(zip(sub["month"], sub[column]))
        return [round(scale * values.get(m, 0.0), 4) for m in months]

    lines: dict[str, dict] = {leg: {} for leg in legs}
    for (leg, line), sub in frame.filter(pl.col("line").is_in(list(wanted))).group_by(
        ["leg", "line"]
    ):
        # P&L sums in basis points of capital; sx = sum of P&L (bp) x book return.
        lines[leg][line] = {
            "s": series(sub, "sum", 1e4),
            "sx": series(sub, "sum_x_book", 1e4),
        }
    doc = {
        "units": "sums of daily P&L in bp of capital; sx = sum of P&L x book return, bp x fraction",
        "months": months,
        "book": {
            "n": book["sessions"].to_list(),
            "s": series(book, "sum", 1e4),
            "sx": series(book, "sum_x_book", 1e4),
        },
        "lines": lines,
        "groups": groups,
    }
    destination.write_text(json.dumps(doc, separators=(",", ":"), ensure_ascii=False))
    return doc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=ASSETS / "attribution-months.json")
    args = parser.parse_args()
    doc = export(args.outputs, args.destination)
    print(f"wrote {args.destination} ({args.destination.stat().st_size / 1e3:.0f} kB, "
          f"{len(doc['months'])} months)")


if __name__ == "__main__":
    main()
