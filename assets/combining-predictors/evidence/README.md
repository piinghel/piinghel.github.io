# Regression article evidence

Aggregate evidence behind the figures and tables of *Combining Multiple Predictors:
The Linear Case*. Security-level data stay in the research project.

## predictor-structure/

The section on how the 80 predictors overlap (Figure 1). Written by
`projects/factor_combination/predictor_structure.py` on the normalized research panel,
every fifth session from 1998 to 2021; the predictor set is the default of the feature
organization (core + standard of every family plus 21-day loss frequency).

- `predictors.csv`: theme, family, sign (of the average IC), mean IC, catalogue
  description and dendrogram leaf position of each predictor, in theme order.
- `predictor_correlation.csv`, `predictor_correlation_yearly.csv`: IC-signed average
  rank correlations, full period and by year (upper triangle).
- `predictor_dendrogram.csv`: average-linkage tree on 1 − |ρ| of the full-period matrix.
- `theme_correlation_yearly.csv`, `theme_ic_yearly.csv`, `theme_ic_daily.csv`:
  correlations and IC of the seven theme composites.

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
  three subsample fits).
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
