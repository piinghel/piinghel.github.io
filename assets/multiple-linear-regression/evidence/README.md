# Ridge article evidence

Aggregate evidence for the fixed three-theme, OLS and Ridge comparison in
*Combining Multiple Predictors: The Linear Case*. These files reproduce
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
- `twelve_input_portfolio_by_schedule.csv` and `twelve_input_portfolio_ranges.csv`
  report the fixed rule and new OLS/Ridge fits on its exact twelve inputs.
  Ranges are the observed minimum and maximum across the three schedules.
  `twelve_input_ranking_summary.csv` uses the same IC definition as Table 2.
- `ranking_sensitivity.csv` compares rankings and daily tail candidates with
  Ridge. Candidate overlap is not inter-rebalance holdings overlap.
- `coefficient_size_and_movement.csv` reports Euclidean coefficient norms and
  changes. `coefficient_direction.csv` checks refit movement after normalizing
  each coefficient vector to unit length.
- `exposure_by_schedule.csv` reports mean daily realized long, short, net and
  gross notionals as percentages of each schedule's fixed capital, valued at
  the close. `exposure_schedule_means.csv` averages those period statistics
  equally across schedules. These are dollar exposures, not market betas.
- `beta_by_schedule.csv` regresses each schedule's saved daily net strategy
  returns on its Russell 1000 benchmark returns, with an intercept, separately
  for each reporting period. `beta_schedule_means.csv` averages the three
  schedule-level estimates equally. Both retain beta before costs as a check,
  R-squared and residual annual volatility. Benchmark returns match daily
  percentage changes in the retained index series exactly; no cash-rate
  adjustment is applied. These constant period betas do not separate stock
  selection, sizing, changing exposures or other factors.
- `spectrum_by_fit.csv` reconstructs the centred predictor covariance for each
  of twelve training windows and three date subsamples from the retained
  normalized cache. Counts use eigenvalue thresholds 0.01 and 0.1; the
  effective degrees of freedom exclude the intercept. Missing targets are
  dropped before assigning date offsets, and covariance is computed in
  float64 from the float32 inputs used by the recorded model configuration.
  Training boundaries match the original OLS log. This diagnostic does not
  recover original training-input hashes or constitute a new model fit.
- `projection_by_refit.csv` projects the saved ensemble-average Ridge minus
  OLS coefficient vector into each refit's pooled valid-target training
  covariance. The bottom half is the 72 smallest eigenvalue directions.
  Coefficient shares use squared Euclidean distance; predictor-variance
  shares use the covariance trace. Article summaries average refits equally.
  This describes the actual ensemble score and does not assume that its
  average weights solve one pooled Ridge objective.
- `low_spectrum_variance_by_member.csv` gives the share of total predictor
  variance in directions with eigenvalues below 0.1 for each of the 36
  separate training fits. These member spectra are distinct from the pooled
  spectrum used for the coefficient projection.

The fixed rule uses twelve ranked predictors in three equally weighted themes:
momentum, defensive characteristics and short positioning. OLS and Ridge in
Tables 2–3 use the same 144 predictors. All three share eligible stock-date
rows and portfolio rules. That benchmark comparison changes both inputs and
weighting; OLS versus Ridge isolates regularization. Table 4 holds the twelve
inputs fixed and changes the weighting, retaining Ridge's MSE penalty c=0.01.

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

For the original 144-input comparison, these rules were checked against the retained matched-study configuration and
the splitter, target filtering, date-subsampling and score-averaging code.
They document the procedure; the aggregates do not verify its original execution.
Original training input content hashes were not captured, and the retained
Ridge training-source record is reconstructed. The successful saved-score
replays validate the portfolio evaluation, not a new model fit.

Displayed predictors are selected by their mean absolute weight
over the full history. Training windows overlap, and later history has informed
research choices. Coefficient persistence is descriptive; these data do not
provide independent coefficient-significance tests.

The original 144-input comparison uses retained predictions; those training
runs have not been independently reproduced. The twelve-input extension was
fitted and evaluated on 14 September 2026 using the retained normalized panel,
with input/configuration hashes and imported code captured during execution.
Its forecast keys, labels, eligibility and twelve window boundaries match
the retained design. A fixed-score control reproduces every score and holding
exactly. Current Float64 price arithmetic changes daily control returns by
at most 1.9e-10 versus the older calculation, below reporting precision;
all three twelve-input scores use the same current execution code. Schedule
metrics were also independently recomputed from the daily returns.

Aggregate evidence reproduces displays and reporting; model fitting also
requires the private research inputs and execution dependencies.

## Predictor structure (80 predictors)

`predictor-structure/` holds the aggregate correlations behind the article's
section on how the predictors overlap: the IC-signed average rank correlation
between the 80 predictors (`predictor_correlation.csv`, in theme order), their
themes and signs (`predictors.csv`), and yearly correlations and ICs of the seven
theme composites. They come from `projects/factor_combination/predictor_structure.py`
on the normalized research panel, every fifth session from 1995 to 2021; the
predictor set is the default of the feature organization (core + standard of
every family plus 21-day loss frequency).
