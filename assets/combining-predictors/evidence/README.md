# Regression article evidence

Aggregate evidence behind the figures and tables of *Combining Multiple Predictors:
The Linear Case*. Security-level data stay in the research project.

## predictor-structure/

The section on how the 80 predictors overlap (Figure 1). Written by
`projects/factor_combination/predictor_structure.py` on the normalized research panel,
every fifth session from 1998 to the last one with a complete 20-session target
(24 April 2026; targets end on 28 April); the predictor set is the default of the
feature organization (core + standard of every family plus 21-day loss frequency).
Signs, predictor order, the full-period matrix and the dendrogram are fitted on
1998–2021 (`--base-end` in the script, `BASE_PERIOD` in the exporter); 2022–2026 reuse
them, and adding years leaves every 1998–2021 value as it was.

- `predictors.csv`: theme, family, sign (of the 1998–2021 average IC), that mean IC,
  catalogue description and dendrogram leaf position of each predictor, in theme order.
- `predictor_correlation.csv`, `predictor_correlation_yearly.csv`: IC-signed average
  rank correlations, 1998–2021 and by year through 2026 (upper triangle).
- `predictor_dendrogram.csv`: average-linkage tree on 1 − |ρ| of the 1998–2021 matrix.
- `theme_correlation_yearly.csv`, `theme_ic_yearly.csv`, `theme_ic_daily.csv`:
  correlations and IC of the seven theme composites.
- `predictor_ic_daily.csv`: rank IC of each predictor with the target on the dates of
  `theme_ic_daily.csv`, one column per predictor in `predictors.csv` order, unsigned;
  the exporter applies the signs. The explorer draws one theme's predictors from it.
  A predictor that is constant across stocks on a date has no rank IC and is written
  as 0, as in the composite (17 cells, all before 2007).

## results/

Tables 2–4, Figures 2–5 and the numbers quoted beside them, from the 2026-09-27
comparison of equal weights with learned weights on the same 80 predictors
(`projects/factor_combination`, outputs `matched_80_20260926/article_2026_09_27`). Every score shares one panel built after
the volatility warm-up and ATR fixes, the same walk-forward (900/21/600, three
interleaved subsample fits), portfolio rule, three rebalance schedules and 5 bp costs.
The equal-weight score gives each predictor 1/80 with the sign of its training-window
correlation with the target; Ridge runs a penalty grid c = 0.01, 0.1, 1, 10, 100
(c = 0 is OLS), and the article uses c = 0.1.

- `ranking_summary.csv`: daily rank IC by score and period (written by `sweep_review.py`).
- `portfolio_table.csv`, `portfolio_by_schedule.csv`: net return, volatility, Sharpe,
  drawdown, market beta, gross exposure and traded notional, as schedule means and per
  schedule.
- `penalty_ic_summary.csv`, `chosen_penalty_by_refit.csv`, `penalty_coefficient_size.csv`:
  IC by penalty, the penalty chosen at each refit from earlier out-of-sample blocks and
  coefficient size relative to OLS (`penalty_validation.py`). The refit dates in the
  second file also draw Figure 2.
- `decile_metrics.csv`: equal-weighted decile portfolios of each score, before costs
  (`prediction_deciles.py`).
- `growth_drawdown.csv`: mean daily net P&L of the three schedules, compounded, with
  drawdowns; the equal-weight and c = 0.1 Ridge rows of the sweep output.
- `ridge_coefficients_by_refit.csv`: c = 0.1 Ridge coefficients per refit (mean of the
  three subsample fits). Figure 6 (similarity to the previous refit and
  coefficient size) is computed from this file by the exporter.
- `score_rank_autocorrelation.csv`, `ols_ridge_score_correlation.csv`: score persistence
  over 15 sessions and the daily OLS–Ridge score correlation.
- `spectrum_by_fit.csv`: eigenvalues of the training covariance per fit (penalty section),
  from `linear_model_diagnostics.py` in `matched_80_20260926/diagnostics`.
- `predictor_return_risk.csv`: IC of size and market-correlation predictors with forward
  return, forward volatility and the target (`predictor_return_risk.py`).
- `book_size_tilt.csv`: average market-cap percentile of the 75 highest and lowest scores
  and the score–size rank correlation (`book_size_tilt.py`).
- `sharpe_difference.csv`: block-bootstrap interval of the Ridge minus equal-weight Sharpe
  difference (`sharpe_difference.py`).
- `low_vol_overlap.csv`: correlation with, and returns next to, the low-volatility
  article's portfolio (`low_vol_overlap.py`).

`scripts/export_predictor_data.py` turns both folders into the JSON files the interactive
figures read.
