"""Risk-concentration article, Figure 1: the largest principal component's share of
forecast variance at every rebalance, with the component's rank.

Reads pca_geometry.csv from the portfolio-optimization risk-concentration review
(projects/portfolio_optimization/outputs/review/risk_concentration) and writes the
aggregate series for the uncapped optimizer on eligible-universe components to
assets/risk-concentration/pc-share.json. The chart itself is drawn in the browser
by assets/js/risk-concentration.js.
"""

import argparse
import csv
import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "assets/risk-concentration/pc-share.json"


def export(geometry: Path) -> None:
    rows = []
    with geometry.open() as source:
        for row in csv.DictReader(source):
            if row["arm"] == "baseline_eligible":
                rows.append((row["date"], float(row["dominant_share"]), int(row["dominant_pc"])))
    rows.sort()
    if not rows:
        raise ValueError("No eligible-universe rows")
    OUTPUT.write_text(json.dumps({
        "dates": [r[0] for r in rows],
        "share_pct": [round(100 * r[1], 2) for r in rows],
        "pc": [r[2] for r in rows],
    }, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, required=True, help="pca_geometry.csv")
    export(parser.parse_args().geometry)
