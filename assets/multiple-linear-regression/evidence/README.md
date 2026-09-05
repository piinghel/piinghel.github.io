# Ridge article evidence

Aggregate evidence for the fixed three-theme, OLS and Ridge comparison in
*Combining Stock Predictors with Linear Regression*. These files reproduce
the article's figures and reported summaries. They contain no stock-level
observations or positions.

From the website repository root:

```bash
python3 -m pip install -r requirements-figures.txt
python3 scripts/render_multiple_linear_regression_figures.py \
  --review-dir assets/multiple-linear-regression/evidence
```

- `multiple_linear_selected_coefficient_heatmap_source_c0p01.csv.gz` contains
  signed coefficients for the ten displayed predictors across twelve refits.
- `multiple_linear_selected_return_drawdown_figure_source.csv.gz` contains the
  common-date mean daily net P&L, its compounded index and drawdown.
- `ranking_summary.csv` reports daily Spearman IC against the sector-ranked
  forward risk-adjusted target, with dates and an unannualized mean/SD ratio.
- `portfolio_by_schedule.csv` retains each starting-week schedule's statistics;
  `portfolio_schedule_means.csv` contains the means used in the article table.
- `ranking_sensitivity.csv` compares rankings and daily tail candidates with
  Ridge. Candidate overlap is not inter-rebalance holdings overlap.
- `coefficient_size_and_movement.csv` reports Euclidean coefficient norms and
  changes. `coefficient_direction.csv` checks refit movement after normalizing
  each coefficient vector to unit length.

The fixed rule uses twelve ranked predictors in three equally weighted themes:
momentum, defensive characteristics and short positioning. OLS and Ridge use
the same 144 predictors. All three share eligible stock-date rows and portfolio
rules. The benchmark comparison changes both inputs and weighting; OLS versus
Ridge isolates regularization.

Portfolio returns are annualized arithmetic means with 252 sessions and 5 bp
per dollar traded. Sharpe uses a zero cash rate. Annual traded notional is
inferred from the gross/net return gap at the recorded proportional cost and
is expressed relative to strategy capital. Drawdowns include the initial
index level. The table averages statistics calculated for each schedule;
the figure compounds the mean of their daily returns on common active dates.
That figure is a fixed-notional performance index.

The model weights in the heatmap are those of the averaged learned score at
each refit. Displayed predictors are selected by their mean absolute weight
over the full history. Training windows overlap, and later history has informed
research choices. Coefficient persistence is descriptive; these data do not
provide independent coefficient-significance tests.

This is a new matched comparison using retained predictions. The original
training runs have not been independently reproduced. Aggregate evidence can
reproduce displays and reporting; model fitting also requires the original
research inputs and execution dependencies.
