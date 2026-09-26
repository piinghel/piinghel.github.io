"""Export the predictor-structure evidence for the regression article's explorer.

Reads the compact CSVs in assets/multiple-linear-regression/evidence/predictor-structure
(written by factor_combination/predictor_structure.py) and writes one JSON file with
yearly IC-signed predictor and theme correlations and the per-date theme IC. Values are
stored as integers (correlation x 1000) to keep the file small; no new statistics are
computed here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "assets/multiple-linear-regression/evidence/predictor-structure"
OUTPUT = ROOT / "assets/multiple-linear-regression/predictor-structure.json"
SHORT_THEMES = {
    "Momentum & trend": "Momentum",
    "Short-term reversal": "Reversal",
    "Volatility": "Volatility",
    "Size": "Size",
    "Liquidity & volume": "Liquidity",
    "Market correlation": "Mkt corr.",
    "Short positioning": "Shorts",
}


def scaled(values, *, scale: int = 1000) -> list[int]:
    return [round(float(v) * scale) for v in values]


def export(evidence: Path, *, short_themes: dict[str, str] = SHORT_THEMES) -> dict:
    predictors = pl.read_csv(evidence / "predictors.csv")
    order = predictors.get_column("predictor").to_list()
    themes = list(dict.fromkeys(predictors.get_column("theme").to_list()))
    theme_index = {t: i for i, t in enumerate(themes)}

    pairs = pl.read_csv(evidence / "predictor_correlation_yearly.csv")
    years = [c for c in pairs.columns if c.isdigit()]
    expected = [(a, b) for i, a in enumerate(order) for b in order[i + 1 :]]
    if list(zip(pairs["predictor_a"], pairs["predictor_b"])) != expected:
        raise ValueError("pair rows must be the upper triangle in predictor order")

    theme_pairs = pl.read_csv(evidence / "theme_correlation_yearly.csv")
    theme_expected = [(a, b) for i, a in enumerate(themes) for b in themes[i + 1 :]]
    theme_rows = {
        int(year): dict(
            zip(zip(group["theme_a"], group["theme_b"]), group["rho"], strict=True)
        )
        for (year,), group in theme_pairs.group_by("year")
    }

    daily = (
        pl.read_csv(evidence / "theme_ic_daily.csv")
        .pivot(on="theme", index="date", values="ic")
        .sort("date")
    )
    if daily.select(themes).null_count().sum_horizontal().item():
        raise ValueError("every sampled date needs an IC for every theme")
    counts = daily.group_by(pl.col("date").str.slice(0, 4).cast(pl.Int64)).len()
    dates_per_year = dict(zip(counts["date"], counts["len"]))

    return {
        "source": "factor_combination/predictor_structure.py; every fifth session",
        "years": [int(y) for y in years],
        "dates_per_year": [int(dates_per_year[int(y)]) for y in years],
        "scale": 1000,
        "themes": [{"name": t, "short": short_themes[t]} for t in themes],
        "predictors": [
            {
                "id": row["predictor"].removeprefix("X_feature_"),
                "theme": theme_index[row["theme"]],
                "description": row["description"],
                "sign": int(row["sign"]),
            }
            for row in predictors.iter_rows(named=True)
        ],
        "predictor_pairs": [scaled(pairs[y]) for y in years],
        "theme_pairs": [
            scaled(theme_rows[int(y)][pair] for pair in theme_expected) for y in years
        ],
        "theme_ic": {
            "dates": daily["date"].to_list(),
            "values": [scaled(row) for row in daily.select(themes).iter_rows()],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = export(args.evidence)
    args.output.write_text(json.dumps(data, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
