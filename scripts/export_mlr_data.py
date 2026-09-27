"""Export the regression article's evidence as JSON for its interactive figures.

predictor-structure.json (Figure 1) comes from evidence/predictor-structure, written by
factor_combination/predictor_structure.py: yearly IC-signed predictor and theme
correlations (x 1000), the dendrogram and the per-date theme IC.
regression-results.json (Figures 3–5) comes from evidence/results, written by
factor_combination's sweep_review.py and prediction_deciles.py: decile statistics,
growth and drawdown of the theme-equal and Ridge scores, and Ridge coefficients by
refit. Only the ten largest coefficients are selected here.
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
# Article names of the compared scores, in display order.
SCORES = {"theme_equal": "Theme-equal", "equal_weight": "Equal-weight", "ols": "OLS", "ridge_0p1": "Ridge"}


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
    growth = pl.read_csv(evidence / "growth_drawdown.csv").sort("date")
    plotted = ["equal_weight", "ridge_0p1"]
    dates = growth.filter(pl.col("model") == plotted[0])["date"].to_list()
    if any(growth.filter(pl.col("model") == m)["date"].to_list() != dates for m in plotted):
        raise ValueError("the plotted scores must share their common dates")
    coefficients = pl.read_csv(evidence / "ridge_coefficients_by_refit.csv")
    top = (
        coefficients.group_by("feature")
        .agg(pl.col("coefficient").abs().mean().alias("size"))
        .sort(["size", "feature"], descending=[True, False])
        .head(10)["feature"]
        .to_list()
    )
    catalogue = pl.read_csv(predictors).select("predictor", "theme", "description")
    info = {row["predictor"]: row for row in catalogue.iter_rows(named=True)}
    years = [
        int(d[:4])
        for d in coefficients.unique("fold_id").sort("fold_id")["test_date"].to_list()
    ]
    deciles = pl.read_csv(evidence / "decile_metrics.csv")
    return {
        "source": "factor_combination sweep_review.py and prediction_deciles.py",
        "dates": dates,
        "growth": {
            SCORES[m]: {
                "growth": [round(float(v), 4) for v in part["growth_index"]],
                "drawdown": [round(float(v), 2) for v in part["drawdown_pct"]],
            }
            for m in plotted
            for part in [growth.filter(pl.col("model") == m)]
        },
        "coefficients": {
            "refit_years": years,
            "predictors": [
                {
                    "label": SHORT_PREDICTORS[f],
                    "description": info[f]["description"],
                    "theme": info[f]["theme"],
                }
                for f in top
            ],
            "values": [
                [
                    round(float(v), 4)
                    for v in coefficients.filter(pl.col("feature") == f).sort("fold_id")["coefficient"]
                ]
                for f in top
            ],
        },
        "deciles": {
            period: {
                SCORES[m]: {
                    metric: [
                        round(float(v), 4)
                        for v in deciles.filter(
                            (pl.col("score") == ("ridge" if m == "ridge_0p1" else m))
                            & (pl.col("period") == period)
                        ).sort("decile")[metric]
                    ]
                    for metric in ("annual_return", "volatility", "sharpe")
                }
                for m in plotted
            }
            for period in ("development", "later")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=ASSETS)
    args = parser.parse_args()
    outputs = {
        "predictor-structure.json": export_structure(args.assets / "evidence/predictor-structure"),
        "regression-results.json": export_results(
            args.assets / "evidence/results",
            args.assets / "evidence/predictor-structure/predictors.csv",
        ),
    }
    for name, data in outputs.items():
        (args.assets / name).write_text(json.dumps(data, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
