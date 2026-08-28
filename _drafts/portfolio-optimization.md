---
layout: post
title: "From Volatility Scaling to State-Aware Portfolio Optimization"
last_modified_at: 2026-08-28
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/portfolio-optimization-preview.html
---

<p class="article-summary">I compare three ways of turning the same Ridge forecasts into a long–short portfolio. Adding correlations and portfolio constraints improves the allocation, but it also increases trading. Making the optimizer aware of current holdings preserves almost all gross performance while cutting annualized turnover from 42.1 to 27.6. Net return rises from 10.77% to 11.62%, and net Sharpe from 1.24 to 1.33. That is the clearest result. Rebalance timing and the calibration of volatility and beta remain the main reasons not to treat the backtest as implementation-ready.</p>

## The portfolio-construction decision

All three portfolios use the same Ridge forecasts. The existing
**volatility-scaled portfolio** selects the 75 strongest forecasts for its long
side and the 75 weakest forecasts for its short side. It gives more weight to
stronger signals and less weight to more volatile stocks.

That rule is a useful baseline, but it does not account for correlations between
holdings, directly constrain portfolio exposures, or consider the positions
already owned. I therefore test two changes:

- The **standard optimizer** adds correlations, a 7% ex-ante volatility budget,
  and limits on name, gross, net, market-beta, and sector exposure.
- The **state-aware optimizer** uses the same risk model and constraints, but
  starts from the current portfolio and discourages unnecessary trading.

The practical question is not whether optimization can make a backtest look
different. It is whether portfolio-level constraints improve the baseline and
whether state awareness retains the improvement after trading costs.

## What stays fixed

The Ridge model uses 144 ranked predictors derived mostly from prices and
returns. It combines them into a ranked forward Sharpe-like score. Every
allocator receives exactly the same saved forecasts and uses the same universe,
execution assumptions, and transaction costs. The comparison therefore tests
portfolio construction rather than a different prediction model.

Forecasts are generated with expanding walk-forward estimation. Results through
2021 are development evidence. January 2022 through May 2026 is a later
pseudo-holdout. Each allocator is run on three staggered rebalance schedules and
pays 5 basis points per dollar traded. The earlier
[Ridge article](/quants/2025/02/09/multiple-linear-regression.html) describes the
prediction model; the
[implementation note](/quants/portfolio-optimization-technical-note.html)
records the exact risk estimates, constraints, and execution rules.

## From a fresh optimum to a portfolio transition

The standard optimizer chooses the highest-scoring portfolio that fits inside
the risk and exposure limits. With $w$ denoting weights, $\mu$ the return scores,
and $\Sigma$ the covariance estimate, the central problem is

$$
\max_w \quad \mu^\top w
\qquad \text{subject to} \qquad
w^\top\Sigma w\leq \sigma_*^2.
$$

The covariance matrix combines 21-session stock-volatility estimates with a
longer, shrunk correlation estimate. This lets the optimizer control total
portfolio risk rather than treating each stock independently. It also imposes
limits on net exposure, market beta, sector exposure, gross exposure, and
individual weights.

The weakness is that every rebalance is solved as if the current portfolio did
not exist. A small change in forecast return can therefore replace an existing
position with a new one.

The state-aware optimizer turns the fresh optimization into a transition from
the current book:

$$
\max_w \quad
\mu^\top w-\lambda\lVert w-w^{-}\rVert_1.
$$

Here $w^{-}$ is the portfolio before rebalancing. The penalty makes a trade
occur only when its forecast benefit is large enough. Fresh positions must
still enter through the top or bottom 75 Ridge ranks, while an existing holding
may remain eligible until it falls beyond rank 175. The coefficient $\lambda$
controls aversion to turnover; it is not an estimate of transaction costs. The
backtest charges those costs separately.

## The main result: similar gross performance, less trading

Across the full history, the standard and state-aware optimizers produce almost
the same gross return: 13.13% and 13.17%. State awareness reduces annualized
turnover from 42.1 to 27.6. The smaller cost drag raises net return from 10.77%
to 11.62% and net Sharpe from 1.24 to 1.33.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annualized turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled portfolio</th><td data-label="Gross return">10.31%</td><td data-label="Net return">8.67%</td><td data-label="Net Sharpe">1.05</td><td data-label="Annualized turnover">29.9</td></tr>
    <tr><th scope="row">Standard optimizer</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Annualized turnover">42.1</td></tr>
    <tr><th scope="row"><strong>State-aware optimizer</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Annualized turnover"><strong>27.6</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Full-history mean across the three rebalance schedules. Annualized turnover is the sum of absolute long and short trades; net returns charge 5 basis points per dollar traded.</p>

The state-aware optimizer's gross-to-net return gap is 1.55 percentage points,
compared with 2.36 points for the standard optimizer. Lower trading costs
therefore explain most of its full-history net advantage.

The penalty and carryover rule reinforce each other. Carryover gives the
optimizer acceptable positions to keep; the penalty gives it a reason to keep
them.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Configuration</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annualized turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">No penalty, no carryover</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Annualized turnover">42.1</td></tr>
    <tr><th scope="row">Carryover only</th><td data-label="Gross return">13.16%</td><td data-label="Net return">10.96%</td><td data-label="Net Sharpe">1.25</td><td data-label="Annualized turnover">39.0</td></tr>
    <tr><th scope="row">Trading penalty only</th><td data-label="Gross return">13.02%</td><td data-label="Net return">11.07%</td><td data-label="Net Sharpe">1.27</td><td data-label="Annualized turnover">34.8</td></tr>
    <tr><th scope="row"><strong>Penalty and carryover</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Annualized turnover"><strong>27.6</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Full-history component test. “Carryover” allows existing holdings to remain eligible through rank 175; without it, every holding must remain in the fresh top or bottom 75.</p>

The interaction adds 0.36 percentage points of net return beyond the sum of the
two changes tested separately. Forced exits still matter: holdings that move
beyond rank 175 must leave, and these exits account for 36% of modeled
state-aware turnover.

## Does the result persist after 2022?

Constrained optimization improves on volatility scaling during development.
Through 2021, the standard optimizer raises annualized net return from 8.92% to
11.60%; state awareness raises it further to 12.32%.

The later period is less favorable. From January 2022 through May 2026, the
standard optimizer falls behind the volatility-scaled portfolio. The
state-aware optimizer remains ahead, with a 7.99% net return and 0.87 net
Sharpe, but the margin is modest.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Net growth of one dollar on a logarithmic scale and drawdowns for the volatility-scaled portfolio, standard optimizer, and state-aware optimizer, with the later period beginning in 2022" version="4" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net cumulative wealth and drawdown for an equal-weight blend of the three rebalance schedules after charging 5 basis points per dollar traded, 22 September 1998–27 May 2026. The vertical rule marks January 2022, the start of the later pseudo-holdout.</p>

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Period</th><th>Portfolio</th><th>Net return</th><th>Net volatility</th><th>Net Sharpe</th><th>Beta</th><th>Max drawdown</th></tr>
  </thead>
  <tbody>
    <tr><td data-label="Period">Through 2021</td><th scope="row">Volatility-scaled</th><td data-label="Net return">8.92%</td><td data-label="Net volatility"><strong>7.92%</strong></td><td data-label="Net Sharpe">1.12</td><td data-label="Beta">0.09</td><td data-label="Max drawdown">19.63%</td></tr>
    <tr><td data-label="Period">Through 2021</td><th scope="row">Standard optimizer</th><td data-label="Net return">11.60%</td><td data-label="Net volatility">8.41%</td><td data-label="Net Sharpe">1.35</td><td data-label="Beta">0.08</td><td data-label="Max drawdown">19.77%</td></tr>
    <tr><td data-label="Period">Through 2021</td><th scope="row"><strong>State-aware</strong></th><td data-label="Net return"><strong>12.32%</strong></td><td data-label="Net volatility">8.40%</td><td data-label="Net Sharpe"><strong>1.43</strong></td><td data-label="Beta"><strong>0.08</strong></td><td data-label="Max drawdown"><strong>18.06%</strong></td></tr>
    <tr><td data-label="Period">2022–May 2026</td><th scope="row">Volatility-scaled</th><td data-label="Net return">7.38%</td><td data-label="Net volatility">9.73%</td><td data-label="Net Sharpe">0.78</td><td data-label="Beta">0.08</td><td data-label="Max drawdown"><strong>8.65%</strong></td></tr>
    <tr><td data-label="Period">2022–May 2026</td><th scope="row">Standard optimizer</th><td data-label="Net return">6.47%</td><td data-label="Net volatility">9.39%</td><td data-label="Net Sharpe">0.71</td><td data-label="Beta">0.02</td><td data-label="Max drawdown">9.41%</td></tr>
    <tr><td data-label="Period">2022–May 2026</td><th scope="row"><strong>State-aware</strong></th><td data-label="Net return"><strong>7.99%</strong></td><td data-label="Net volatility"><strong>9.32%</strong></td><td data-label="Net Sharpe"><strong>0.87</strong></td><td data-label="Beta"><strong>0.01</strong></td><td data-label="Max drawdown">9.05%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> Mean of schedule-level metrics. The development period runs from each schedule's September 1998 start through 2021; the later pseudo-holdout runs from January 2022 through 27 May 2026.</p>

Two caveats belong next to this result. First, the three state-aware schedules
produce a 4.49-percentage-point spread in later-period net return and a 0.43
spread in Sharpe. Rebalance timing is therefore economically important. Second,
the period after 2022 is only a pseudo-holdout: it was separated from the
original development period, but later research choices were made with some
knowledge of it.

## The constraints control forecasts, not outcomes

The return and turnover evidence favors state awareness. Risk calibration is
less reassuring.

At every rebalance, Figure 2 compares predicted annualized volatility with
volatility realized before the next execution. A calibrated forecast would lie
near the diagonal. Instead, the standard and state-aware forecasts cluster near
their 7% budget while realized risk varies much more. Across all rebalances,
their root-mean-square realized volatility is 8.6%.

<div class="research-figure risk-forecast-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-forecast-through-time" alt="Scatter plots of predicted and subsequently realized annualized volatility at every rebalance for the volatility-scaled portfolio, standard optimizer, and state-aware optimizer" version="3" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Predicted versus subsequently realized annualized volatility at every rebalance across all three schedules. The diagonal marks perfect calibration. The shared axes focus on the regular range; triangles mark the 10, 12, and 11 realized observations above 20%, whose maxima are 48.9%, 34.7%, and 34.3%.</p>

### Beta is measured on several different clocks

The beta evidence needs more care than the earlier version of this article gave
it. The optimizer and the diagnostics do not use the same horizon:

<table class="research-table methodology-table portfolio-card-table">
  <thead>
    <tr><th>Quantity</th><th>Window</th><th>Purpose</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Optimizer beta</th><td data-label="Window">756-day stock–market correlation; 21-day volatility ratio</td><td data-label="Purpose">Constrains target weights at each rebalance</td></tr>
    <tr><th scope="row">Holding-period beta</th><td data-label="Window">Next 10–14 trading days</td><td data-label="Purpose">Matches execution-to-execution returns, but is noisy</td></tr>
    <tr><th scope="row">Forward diagnostic</th><td data-label="Window">Next 21 trading days</td><td data-label="Purpose">Tests beta forecasts near the trading horizon</td></tr>
    <tr><th scope="row">Figure 3 beta</th><td data-label="Window">Trailing 252 trading days</td><td data-label="Purpose">Shows the portfolio's slower realized market sensitivity</td></tr>
  </tbody>
</table>

The distinction changes the conclusion. During 2026, the state-aware target
beta averages +0.050. Execution moves the model beta by about 0.009 on average,
and subsequent holdings drift moves it by about 0.016. Those effects are real,
but small relative to the 0.236 mean absolute gap between target beta and beta
realized over the following holding period.

The separate 21-day diagnostic tells the same story. Its realized beta averages
about +0.20 in the recent window even though target beta remains near +0.05.
Across the full history, target beta and forward 21-day realized beta have only
a 0.16 correlation. The main problem is therefore beta estimation, not simply
execution delay or price drift.

Figure 3 answers a different question. It shows the slower 252-day beta path and
should not be read as a direct test of the point-in-time constraint. At the end
of May 2026, the mean across schedules is about +0.071 for the standard
optimizer and +0.045 for the state-aware optimizer.

<div class="research-figure realised-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/realised-beta" alt="Rolling 252-day realized beta for the volatility-scaled portfolio, standard optimizer, and state-aware optimizer" version="2" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Trailing 252-day realized beta, sampled monthly and averaged across the three staggered schedules. This is a slow outcome measure, not the beta estimate constrained at each rebalance.</p>

The next beta study should compare the current hybrid estimator with a coherent
252-day estimator and a fixed 252/756-day blend. The choice should be frozen on
pre-2022 mean absolute beta error and tail error, then evaluated after 2022. A
shorter window may adapt faster, but it should earn its place through forecast
calibration rather than a better in-sample Sharpe.

## Conclusion

State awareness is the version I would carry forward. It preserves the standard
optimizer's gross performance while eliminating enough trading to improve net
return and Sharpe. The component test also gives the result a plausible
mechanism: carryover supplies acceptable incumbent positions, and the penalty
makes replacing them costly.

That conclusion is narrower than saying the allocator is ready for live use.
The later-period advantage is sensitive to rebalance timing, realized volatility
does not stay close to the ex-ante budget, and the current beta estimator has
weak forward calibration. The next research step is therefore not another
return-model sweep. It is a predeclared beta-window comparison and continued
evaluation on genuinely new data.
