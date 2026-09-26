"""Export the regression article's evidence as JSON for its interactive figures.

predictor-structure.json (Figure 1) comes from evidence/predictor-structure, written by
factor_combination/predictor_structure.py: yearly IC-signed predictor and theme
correlations (x 1000), the dendrogram and the per-date theme IC.
regression-results.json (Figures 3 and 4) comes from evidence/results, written by
factor_combination/linear_model_diagnostics.py: growth and drawdown of the three scores
and the ten largest Ridge coefficients per refit. No statistics are computed here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/multiple-linear-regression"
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


def export_structure(evidence: Path, *, short_themes: dict[str, str] = SHORT_THEMES) -> dict:
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

    tree = pl.read_csv(evidence / "predictor_dendrogram.csv")

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
                "leaf": int(row["dendrogram_leaf"]),
            }
            for row in predictors.iter_rows(named=True)
        ],
        "dendrogram": {
            "positions": [[round(float(v), 1) for v in r] for r in tree.select(r"^position_\d$").iter_rows()],
            "heights": [[round(float(v), 4) for v in r] for r in tree.select(r"^height_\d$").iter_rows()],
        },
        "predictor_pairs": [scaled(pairs[y]) for y in years],
        "theme_pairs": [
            scaled(theme_rows[int(y)][pair] for pair in theme_expected) for y in years
        ],
        "theme_ic": {
            "dates": daily["date"].to_list(),
            "values": [scaled(row) for row in daily.select(themes).iter_rows()],
        },
    }


def export_results(evidence: Path) -> dict:
    growth = pl.read_csv(evidence / "figure3_growth_drawdown.csv").sort("date")
    series = list(dict.fromkeys(growth["series"].to_list()))
    dates = growth.filter(pl.col("series") == series[0])["date"].to_list()
    if any(growth.filter(pl.col("series") == n)["date"].to_list() != dates for n in series):
        raise ValueError("the three scores must share their common dates")
    top = pl.read_csv(evidence / "ridge_top10_coefficients.csv").sort("rank")
    refits = pl.read_csv(evidence / "ridge_coefficients_by_refit.csv")
    years = [
        int(d[:4])
        for d in refits.unique("fold_id").sort("fold_id")["test_date"].to_list()
    ]
    rows = []
    for feature in top["feature"].to_list():
        coef = refits.filter(pl.col("feature") == feature).sort("fold_id")["coefficient"]
        if coef.len() != len(years):
            raise ValueError(f"{feature}: expected one coefficient per refit")
        rows.append([round(float(v), 4) for v in coef])
    return {
        "source": "factor_combination/linear_model_diagnostics.py",
        "dates": dates,
        "growth": {
            name: {
                "growth": [round(float(v), 4) for v in group["growth_index"]],
                "drawdown": [round(float(v), 2) for v in group["drawdown_pct"]],
            }
            for name in series
            for group in [growth.filter(pl.col("series") == name)]
        },
        "coefficients": {
            "refit_years": years,
            "predictors": [
                {"description": d, "theme": t}
                for d, t in zip(top["description"], top["theme"])
            ],
            "values": rows,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=ASSETS)
    args = parser.parse_args()
    outputs = {
        "predictor-structure.json": export_structure(args.assets / "evidence/predictor-structure"),
        "regression-results.json": export_results(args.assets / "evidence/results"),
    }
    for name, data in outputs.items():
        (args.assets / name).write_text(json.dumps(data, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
