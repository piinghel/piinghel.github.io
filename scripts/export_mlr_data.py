"""Export the regression article's evidence as JSON for its interactive figures.

predictor-structure.json (Figure 1) comes from evidence/predictor-structure, written by
factor_combination/predictor_structure.py: yearly IC-signed predictor and theme
correlations (x 1000), the dendrogram and the per-date theme IC.
coefficients.json (Figure 5) contains all coefficients by refit, ranked by magnitude.
Performance and daily deciles are exported by export_regression_charts.py.
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
# Figure 5 row labels; the full catalogue description stays in the hover.
SHORT_PREDICTORS = {
    "X_feature_price_macd_10_21": "MACD 10/21",
    "X_feature_short_interest_to_volume_log_ratio": "Days to cover",
    "X_feature_price_sharpe_ratio_compound_r126_volatility126_rolling": "Sharpe 126d",
    "X_feature_pv_illiquidity_mean21": "Amihud illiquidity 21d",
    "X_feature_price_high_to_initial90_exclude10": "90d high / start price",
    "X_feature_market_cap_log_std504": "Mcap variability 504d",
    "X_feature_liquidity_turnover_level63": "Share turnover 63d",
    "X_feature_price_ret252_shift0": "Return 252d",
    "X_feature_market_cap_log_std21": "Mcap variability 21d",
    "X_feature_price_atr5": "Average true range 5d",
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


def export_results(evidence: Path, predictors: Path) -> dict:
    coefficients = (
        pl.scan_csv(evidence / "ridge_coefficients_by_refit.csv")
        .sort("fold_id")
        .group_by("feature")
        .agg(
            pl.col("coefficient").abs().mean().alias("size"),
            pl.col("coefficient"),
            pl.col("test_date"),
        )
        .sort(["size", "feature"], descending=[True, False])
        .collect()
    )
    ranked = coefficients["feature"].to_list()
    refit_dates = coefficients["test_date"].to_list()
    if not refit_dates or any(dates != refit_dates[0] for dates in refit_dates):
        raise ValueError("Every predictor must cover the same refit dates")
    catalogue = pl.scan_csv(predictors).select("predictor", "theme", "description").collect()
    info = {row["predictor"]: row for row in catalogue.iter_rows(named=True)}
    years = [int(d[:4]) for d in refit_dates[0]]
    return {"version": 1, "charts": {"coefficients": {
            "kind": "matrix", "unit": "Coefficient", "defaultCount": 10,
            "columns": [str(year) for year in years],
            "rows": [SHORT_PREDICTORS.get(f, info[f]["description"]) for f in ranked],
            "descriptions": [info[f]["description"] + " · " + info[f]["theme"] for f in ranked],
            "values": [
                [round(float(value), 4) for value in values]
                for values in coefficients["coefficient"].to_list()
            ],
        }}}



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=ASSETS)
    parser.add_argument("--evidence", type=Path, help="Retained aggregate CSV directory")
    args = parser.parse_args()
    evidence = args.evidence or args.assets / "evidence"
    outputs = {
        "predictor-structure.json": export_structure(evidence / "predictor-structure"),
        "coefficients.json": export_results(
            evidence / "results",
            evidence / "predictor-structure/predictors.csv",
        ),
    }
    for name, data in outputs.items():
        (args.assets / name).write_text(json.dumps(data, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
