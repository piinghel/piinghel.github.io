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

The recorded training configuration uses an expanding history beginning in
January 1995: 900 initial trading dates, a 21-date gap, then a 600-date
prediction block. Each refit adds 600 dates to the history and preserves the
gap; the final prediction block is shorter. With one-based date indices,
the first training window is 1–900, the gap is 901–921, and prediction covers
922–1521. The second training window is 1–1500 and prediction starts at 1522.
The target requires 20 forward returns, and missing targets are dropped from
training. Prediction rows need no observed target; IC uses complete targets.

Each OLS or Ridge refit fits three members on complementary date samples:
1, 4, 7, …; 2, 5, 8, …; and 3, 6, 9, … within the training history after
dropping missing targets. Each member predicts every row in the next block.
Their predicted scores are averaged with equal weights before ranking. This
equals a linear score with the mean intercept and mean coefficient vector.
The heatmap and coefficient diagnostics use that mean vector at each refit,
not an average across refits or across portfolio schedules. Date thinning
still leaves overlapping 20-session outcomes within and between members.

These rules were checked against the retained matched-study configuration and
the splitter, target filtering, date-subsampling and score-averaging code.
They document the procedure; the aggregates do not verify its original execution.
Original training input content hashes were not captured, and the retained
Ridge training-source record is reconstructed. The successful saved-score
replays validate the portfolio evaluation, not a new model fit.

Displayed predictors are selected by their mean absolute weight
over the full history. Training windows overlap, and later history has informed
research choices. Coefficient persistence is descriptive; these data do not
provide independent coefficient-significance tests.

This is a new matched comparison using retained predictions. The original
training runs have not been independently reproduced. Aggregate evidence can
reproduce displays and reporting; model fitting also requires the original
research inputs and execution dependencies.
