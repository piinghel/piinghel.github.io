---
layout: post
title: "From Volatility Scaling to Joint Sizing"
description: "Sizing stocks together under a risk budget, then slowing the trading down with a rank buffer and a trade penalty."
date: 2026-08-29
last_modified_at: 2026-09-26
categories: ["Portfolio construction"]
article_label: Portfolio construction · Joint sizing
permalink: /quants/2026/08/29/portfolio-optimization.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/portfolio-optimization-study
---

In the articles on [low-volatility sizing](/quant/2024/12/15/low-volatility-factor.html)
and [combining predictors](/quants/2025/02/09/multiple-linear-regression.html),
I sized positions one stock at a time: scale each by its own volatility and
cap it. That simple rule worked well. Here I want to see whether sizing the
stocks together, taking into account how they move with each other, does
better once trading costs are included.

Joint sizing brings two new problems. The optimizer can lean on combinations
that look safer than they are, and it can trade a lot in response to small
changes in its inputs. I use correlation shrinkage for the first and a rank
buffer plus a trade penalty for the second.

The setup follows the [combining-predictors article](/quants/2025/02/09/multiple-linear-regression.html#portfolio-construction):
the same universe and Ridge ranking, 75 long and 75 short names, three
rebalance schedules that each trade every three weeks starting a week apart,
next-close execution and 5 bp per dollar traded. I choose settings on
September 1998–December 2021 (development) and report January 2022–May 2026
separately. Tables show the mean of metrics calculated separately for each
schedule. Returns are geometric and annualized; Sharpe uses the arithmetic
mean daily return and a zero risk-free rate; turnover is two-way, relative to
strategy capital and annualized; drawdowns are maximum peak-to-trough losses.

## Why size jointly

Start with the unconstrained problem. With expected excess returns
$$\alpha$$ and a positive-definite covariance matrix $$\Sigma$$,

$$
\max_{w\ne0}\frac{\alpha^\top w}{\sqrt{w^\top\Sigma w}},
\qquad w^\star\propto\Sigma^{-1}\alpha.
$$

Scaling all positions by a positive constant scales expected return and
volatility equally, so Sharpe fixes the relative weights and leaves the size
of the portfolio open. Without other limits, I could pick the direction first
and then lever it to any volatility I want.

Portfolio limits break that separation. Scaling from 5% to 7% forecast
volatility turns a 4% position into 5.6% and breaches the name cap. So I put
the volatility budget inside the optimization rather than scaling afterwards.

My inputs are relative scores, not calibrated expected returns. For each
stock I multiply its Ridge prediction $$s_{i,t}$$ by its estimated daily
volatility $$\widehat\sigma_{i,t}$$ to get a *sizing score*
$$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$. The Ridge target ranks forward
return divided by volatility, so this puts the scores back on each stock's
risk scale.[^ranking] With signed weights $$w_t$$ and volatility target
$$\sigma_{\mathrm{target}}$$, I solve

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq \sigma_{\mathrm{target}}^2,\\
& w_t\in\mathcal W_t,
\end{aligned}
$$

where $$\Sigma_t$$ is the annualized forecast covariance matrix and
$$\mathcal W_t$$ holds the other portfolio limits. I use a 7% target. Once
those limits bind, maximizing the score is no longer the same as maximizing
Sharpe, and forecast volatility can end up below 7%.

## Covariance and correlation shrinkage
{: #covariance-and-risk-forecasts }

The optimizer is only as good as $$\Sigma_t$$. I let each stock's volatility
react faster than the correlations: 21-day volatility, 756-day correlations of
volatility-standardized returns. The raw correlation estimate needs some
repair before it is a valid correlation matrix (appendix). I then shrink the
repaired estimate $$\widetilde R_t$$ toward the identity matrix:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I.
$$

At $$\rho=0$$ I keep the estimated correlations; at $$\rho=1$$ I discard
them. I use $$\rho=0.5$$, which halves every off-diagonal correlation and
leaves each stock's own variance unchanged.

The reason to shrink is clearest in principal components, as Pedersen, Babu
and Levine explain in
[*Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543)
(2021, pp. 129–130). Each component is a combination of
volatility-standardized returns with unit-length eigenvector $$q_j$$ and
estimated variance $$\lambda_j$$. Shrinkage keeps the eigenvectors and gives

$$
\begin{aligned}
\lambda_j(\rho)&=(1-\rho)\lambda_j+\rho,\\
C(\rho)^{-1}q_j&=\frac{q_j}{\lambda_j(\rho)}.
\end{aligned}
$$

The eigenvalues move toward their average of one: small ones rise and large
ones fall. Because the inverse divides each component by its estimated
variance, a favorable score in a low-variance direction attracts a large
allocation, and an underestimated variance amplifies the error in that score
too. Shrinking gives up some of the most attractive-looking diversification
in exchange for weights that are less sensitive to estimation error.

The covariance matrix and its inverse, the *precision matrix*, are

$$
\begin{aligned}
\Sigma_t&=D_tC_t(\rho)D_t,\\
\Sigma_t^{-1}&=D_t^{-1}C_t(\rho)^{-1}D_t^{-1},
\end{aligned}
$$

with $$D_t$$ the diagonal matrix of annualized volatility forecasts. Read
right to left, the precision matrix divides expected returns by volatility,
adjusts them for correlation, and converts back to weights. At full
shrinkage, the sizing scores cancel one volatility factor and the weights
become proportional to $$s_{i,t}/\widehat\sigma_{i,t}$$: volatility scaling
again, apart from the portfolio limits. Joint sizing is the same idea with
correlations added back in.

*Risk calibration* is the square root of mean realized holding-period
variance divided by mean forecast variance at execution; one means forecast
and realized risk agree. The volatility forecasts in $$D_t$$ include a
multiplier that corrects their average bias. I estimate it on complete
holding periods ending by December 2021, so that development risk
calibration is close to one. It comes out at [TBD]. With it, the optimizer
with trading controls realizes [TBD] volatility in development against the
7% target.[^calibration]

Figure 1 shows why I keep some estimated correlation. I rebuild the
optimizer, with and without the trading controls described below, at each
shrinkage value using development data.

<div class="research-figure rho-ladder-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" mobile="/assets/portfolio-optimization/rho-ladder_mobile" alt="Four panels showing risk calibration, holding-period beta error, annual turnover, and net Sharpe across correlation shrinkage for both optimizers, with the 0.3 to 0.6 region shaded" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 1: Correlation shrinkage.</strong> Risk calibration, mean absolute holding-period beta error, annual turnover and net Sharpe at each shrinkage value, development period. The shaded band marks 0.3–0.6; the selected value is 0.5.</p>

[TBD: how calibration, beta error, turnover and Sharpe move from 0.3 to 0.6,
and at zero and full shrinkage.]

Factor models are the other standard route to a covariance matrix, and they
combine with shrinkage in the same optimizer. I stick with empirical
correlations here. For an introduction I liked HRT's
[*Modeling Equities Returns: The Linear Case*](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/)
and Chapter 4 of Giuseppe Paleologo's
[*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6).

## Constraints as intentions

Each limit in $$\mathcal W_t$$ is there to stop a specific failure:

- Gross exposure (200%) stops the optimizer from levering up low-risk
  combinations to reach the volatility target.
- Net exposure (±25%) keeps the portfolio close to long–short, so returns
  come mainly from selection rather than market direction.
- The name limit (4%) caps the damage from one bad forecast or one
  underestimated volatility.
- Estimated beta (±0.05) limits market exposure at each rebalance.
- Sector limits (±20% net, 30% of either book) stop a sector bet from
  building up through correlated stock scores.

Long candidates can take positive or zero weights and short candidates
negative or zero weights, so the optimizer sizes the selected names but
cannot flip their side. The limits apply to target weights; the appendix
covers how holdings drift between rebalances.

## Step by step
{: #development-results }

Table 1 builds from the combining-predictors rule to the final portfolio,
one change at a time, with the same Ridge ranking throughout. The first row
is that article's evaluation rule: equal signal weights within each book,
scaled by volatility. The second gives stronger scores larger signal weights.
The third sizes the stocks jointly, and the fourth adds the trading controls.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: From volatility scaling to joint sizing.</strong> Development period, September 1998–December 2021.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Max drawdown</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled, equal signal weights</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Optimizer</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

Weighting by score takes Sharpe from [TBD] to [TBD]. Joint sizing adds
[TBD] points of gross return and lifts Sharpe to [TBD], but turnover rises
from [TBD]× to [TBD]× a year. The trading controls keep [TBD] of that gross
return and bring turnover down to [TBD]×, for a Sharpe of [TBD].

Joint sizing changes the covariance, the score scaling and the constraints at
once, so the third row compares full rules rather than isolating each change.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" mobile="/assets/portfolio-optimization/performance-and-drawdowns_mobile" alt="Development-period net growth and drawdowns for the portfolio rules" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 2: Development-period growth and drawdowns.</strong> Net growth index (log scale) and drawdown after trading costs, September 1998–December 2021. Each path averages three separately compounded schedules at the rule's own volatility.</p>

[TBD: where the lead opens in Figure 2.]

## Trading controls

At each rebalance, the basic optimizer starts from the newly selected
stocks. A small change in rank or covariance can trigger a replacement whose
benefit is smaller than its cost.

Take a long stock whose rank slips from 60 to 110. The basic optimizer drops
it, because only the top 75 enter the new selection. With a *rank buffer*,
existing holdings stay eligible through rank 175 (the short book uses the
matching bottom ranks). Holdings outside that range are still closed.

The buffer only keeps a holding eligible; the trade penalty makes keeping it
the default. With $$w_t^{\mathrm{pre}}$$ the weights just before rebalancing
and *trade coefficient* $$c$$, the objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

under the same constraints and risk budget. The L1 term counts both sides of
a replacement: selling one 1% position to buy another adds 2% to
$$\lVert w_t-w_t^{\mathrm{pre}}\rVert_1$$. The optimizer keeps the existing
holding unless the new position's score clears that hurdle or the old one
breaches a limit. Because the penalty is in score units, multiplying all
scores by $$a$$ is the same as dividing $$c$$ by $$a$$, so
$$c=2.5\times10^{-4}$$ only means something relative to these scores. The
5 bp cost is charged separately on executed trades.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: What each trading control contributes.</strong> Development period, September 1998–December 2021.</caption>
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annual turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Neither control</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="selected-rule"><th scope="row">Buffer + penalty</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

The buffer alone saves about [TBD] times capital a year; together with the
penalty the saving is [TBD]. I use both because they work together: the
buffer keeps more holdings eligible and the penalty favors keeping them.

Figure 3 varies one control at a time around the chosen settings.

<div class="research-figure parameter-sensitivity-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" mobile="/assets/portfolio-optimization/parameter-sensitivity_mobile" alt="Development-period net Sharpe and annualized turnover for six trade coefficients and five holding-rank cutoffs" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 3: Sensitivity to the trading controls.</strong> Development-period net Sharpe and annual turnover for six trade coefficients (in units of 10<sup>−4</sup>) and five rank cutoffs. Points are schedule means; whiskers span the three schedules. Chosen settings are highlighted.</p>

[TBD: the coefficient plateau and the choice of 2.5; rank cutoffs 150–200 and
the choice of 175.]

## After 2021

Table 3 covers January 2022–May 2026, about four and a half years.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: The same rules after 2021.</strong> January 2022–May 2026.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Max drawdown</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled, equal signal weights</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Optimizer</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: how the four rules compare after 2021.]

The average hides a large spread across rebalance schedules. With trading
controls, net return differs by [TBD] points between the best and worst
schedule, against [TBD] for score-weighted volatility scaling. Trading more
slowly still helps on average, but much less consistently than in
development. Combining the rebalance weeks is one way to reduce that
dependence; I look at it in [TBD: link to the tranching article once it is
published].

Much of the weakness comes from the short book in December 2022–February
2023. For the three schedules combined, the long book contributes about
[TBD] percentage points and the short book [TBD], as sums of daily after-cost
contributions. The [attribution series](/quants/portfolio-attribution.html)
looks at why short books struggle in rebounds.

## Forecast beta versus realized beta

The beta limit applies to an estimate at each rebalance. Figure 4 tracks
the beta of the portfolio's realized returns over a trailing year, which
reflects holdings and market moves throughout that year.

<div class="research-figure risk-beta-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" mobile="/assets/portfolio-optimization/risk-calibration-and-beta_mobile" alt="Trailing 252-day realized market beta for the portfolio rules during development" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4: Realized beta.</strong> Month-end trailing 252-day market beta, averaged across the three schedules, September 1999–December 2021.</p>

Joint sizing shortens the long departures from zero seen under volatility
scaling, but several episodes still last for months and reach [TBD]. The
rebalance-time estimate also misses over individual holding periods. This is
the main weakness I haven't solved; a shorter beta window didn't fix it
(appendix).

## What joint sizing buys, and what it costs

In development, joint sizing with trading controls lifts Sharpe from [TBD]
for the combining-predictors rule to [TBD], and maximum drawdown goes from
[TBD] to [TBD]. [TBD: which step contributes most.]

The cost is complexity and, without controls, turnover. The optimizer needs a
covariance estimate, a shrinkage choice, a risk multiplier and a set of
constraints, and on its own it trades [TBD]× capital a year against [TBD]×
for volatility scaling. [TBD: whether the controls remove all of the extra
trading, and whether I'd use the optimizer without them.]

Two problems remain. Realized beta drifts well away from the rebalance-time
estimate for months at a time, and after 2021 the result depends heavily on
the rebalance schedule. The second is partly a sampling problem, which
combining schedules addresses; the first needs a better beta forecast.

## Appendix

### Allocation settings

<table class="research-table settings-table">
  <caption><strong>Table 4: Allocation settings.</strong></caption>
  <thead><tr><th>Component</th><th>Setting</th></tr></thead>
  <tbody>
    <tr><th scope="row">Selection</th><td>75 long + 75 short; with the buffer, existing holdings stay eligible through rank 175</td></tr>
    <tr><th scope="row">Volatility-scaled rules</th><td>Equal or logistic (slope 2) signal weights; 60-day volatility, 20% reference and 5% floor; 4% name cap; each book scaled down above 100% gross</td></tr>
    <tr><th scope="row">Joint portfolio limits</th><td>7% forecast volatility; 200% gross; 4% per name; ±25% net; ±0.05 estimated beta</td></tr>
    <tr><th scope="row">Sector limits</th><td>±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Covariance estimate</th><td>21-day volatility; 756-day correlations of volatility-standardized returns (252 observations minimum); 50% shrinkage toward identity; volatility multiplier [TBD], estimated on development data</td></tr>
    <tr><th scope="row">Beta estimate</th><td>756-day correlation with the market (252 observations minimum) combined with 21-day stock and market volatility</td></tr>
    <tr><th scope="row">Trade penalty</th><td><i>c</i> = 2.5 × 10<sup>−4</sup> on the absolute change from drifted pre-trade weights</td></tr>
  </tbody>
</table>

### Correlation-matrix preparation

Daily returns are capped at ±30% before estimating correlations, and pairs
without enough overlapping history use a correlation of 0.50. The resulting
matrix is symmetrized, negative eigenvalues are clipped to zero and the unit
diagonal is restored, all before shrinkage.

### Targets, drift and costs

All limits apply to target weights at the rebalance. After next-close
execution and later price moves, holdings can drift outside them until the
next rebalance. The trade penalty measures changes from these drifted
pre-trade weights, and costs are charged on executed trades. At [TBD]×
annual turnover, 5 bp costs about [TBD]% of strategy capital a year on an
arithmetic basis; the gap between gross and net geometric returns also
includes compounding.

### A shorter beta window

I tried a 63-day beta window, keeping everything else the same. It removes
the persistent episodes in Figure 4, but [TBD: result with trading controls
and the decision against my 0.5-point net-return tolerance].

[^ranking]: Ranking removes the return magnitudes, so the sizing score is a relative measure, not an expected return.
[^calibration]: A different multiplier also changes the weights, including which constraints bind and how much the portfolio trades, so every result here uses the recalibrated forecasts.
