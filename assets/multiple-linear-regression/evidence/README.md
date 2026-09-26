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

Tables 2–4, Figures 3–4 and the appendix, from the matched rerun of the fixed score,
OLS and Ridge on the 80 predictors and on the fixed score's twelve inputs
(`projects/factor_combination`, outputs `matched_80_20260926`, registry experiment
`factor-combination:exp:matched-80-predictors`). All scores share one panel built after
the volatility warm-up and ATR fixes, the same walk-forward (900/21/600, three
interleaved subsample fits), portfolio rules, three rebalance schedules and 5 bp costs.

- `ranking_summary.csv`, `twelve_input_ranking_summary.csv`: daily rank IC.
- `portfolio_table.csv`, `portfolio_by_schedule.csv`: net and gross return, volatility,
  Sharpe, drawdown, market beta, gross and net exposure, traded notional and cost drag,
  as schedule means and per schedule.
- `figure3_growth_drawdown.csv`: mean daily net P&L of the three schedules on common
  dates, compounded, with drawdowns.
- `ridge_coefficients_by_refit.csv`, `ridge_top10_coefficients.csv`: Ridge
  coefficients per refit (mean of the three subsample fits) and the ten largest.
- `coefficient_size_and_movement.csv`, `spectrum_by_fit.csv`, `projection_by_refit.csv`:
  the appendix on what Ridge changes.
- `score_rank_autocorrelation.csv`, `theme_rank_autocorrelation.csv`,
  `short_horizon_weight_share.csv`, `theme_weight_share.csv`: the turnover discussion.
- `fixed_data_fix_portfolio.csv`: effect of the data fixes on the fixed score.

`scripts/export_mlr_data.py` turns both folders into the JSON files the interactive
figures read.
