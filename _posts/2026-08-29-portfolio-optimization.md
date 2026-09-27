---
layout: post
title: "From Volatility Scaling to Joint Sizing"
description: "Sizing stocks together under a risk budget, then slowing the trading down with a rank buffer and a trade penalty."
date: 2026-08-29
last_modified_at: 2026-09-27
categories: ["Portfolio construction"]
article_label: Portfolio construction · Joint sizing
permalink: /quants/2026/08/29/portfolio-optimization.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/portfolio-optimization-study
---

In the articles on [low-volatility sizing](/quant/2024/12/15/low-volatility-factor.html)
and [linear regression](/quants/2025/02/09/multiple-linear-regression.html),
I sized positions one stock at a time: scale each by its own volatility and
cap it. That simple rule worked well. Here I want to see whether sizing the
stocks together, taking into account how they move with each other, does
better once trading costs are included.

Joint sizing brings two new problems. The optimizer can lean on combinations
that look safer than they are, and it can trade a lot in response to small
changes in its inputs. I use correlation shrinkage for the first and a rank
buffer plus a trade penalty for the second.

The setup follows the [regression article](/quants/2025/02/09/multiple-linear-regression.html#portfolio-construction):
the same universe and Ridge ranking, 75 long and 75 short names, three
rebalance schedules that each trade every three weeks starting a week apart,
and next-close execution. I charge 5 bp per dollar traded and ignore borrow,
financing and market impact. I choose settings on September 1998–December
2021 (development) and report January 2022–May 2026 separately.

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
the volatility budget inside the optimization. A risk penalty
$$\lambda w^\top\Sigma w$$ in the objective would give the same solutions for
some $$\lambda$$, but a hard budget sets the risk directly in volatility units.

My inputs are relative scores, not calibrated expected returns. For each
stock I multiply its Ridge prediction $$s_{i,t}$$ by its estimated daily
volatility $$\widehat\sigma_{i,t}$$ to get a *sizing score*
$$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$. This is the familiar
$$\alpha=\mathrm{IC}\cdot\sigma\cdot\text{score}$$ form with one IC for all
stocks, which only rescales the scores. With signed weights $$w_t$$ and
volatility target $$\sigma_{\mathrm{target}}$$, I solve

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq \sigma_{\mathrm{target}}^2,\\
& w_t\in\mathcal W_t,
\end{aligned}
$$

where $$\Sigma_t$$ is the annualized forecast covariance matrix and
$$\mathcal W_t$$ holds the other portfolio limits. I use a 7% target, close to
the [TBD] realized volatility of volatility scaling in development. Once the
other limits bind, maximizing the score is no longer the same as maximizing
Sharpe, and forecast volatility can end up below 7%.

## Covariance and correlation shrinkage
{: #covariance-and-risk-forecasts }

The optimizer is only as good as $$\Sigma_t$$. I use empirical correlations
because they leave a single choice to make, the shrinkage. Each stock's
volatility reacts faster than the correlations: 21-session volatility,
756-session correlations of volatility-standardized returns. The raw
correlation estimate needs some repair before it is a valid correlation
matrix (appendix). I then shrink the repaired estimate
$$\widetilde R_t$$ toward the identity matrix:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I.
$$

At $$\rho=0$$ I keep the estimated correlations; at $$\rho=1$$ I discard
them. I use $$\rho=0.5$$, which halves every off-diagonal correlation and
leaves each stock's own variance unchanged. Halving the correlations also
halves their average, so the model understates common risk; part of what the
volatility multiplier below corrects may come from this. A constant-correlation
target would keep the average.

I like the explanation of shrinkage through principal components in Pedersen,
Babu and Levine's
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
and realized risk agree. I expect an optimized portfolio to under-forecast
its risk, because the optimizer seeks out the directions whose estimated risk
is lowest, and those are the ones most likely to be underestimated. The
volatility forecasts in $$D_t$$ therefore include a multiplier, which I
estimate on complete holding periods ending by December 2021. It comes out at
[TBD]. That makes development calibration close to one by construction, so
the test is the later period (Table 3).[^calibration]

Figure 1 shows why I keep some estimated correlation. I rebuild the optimizer
at each shrinkage value using development data, with and without the trading
controls described below (a rank buffer and a trade penalty).

<div class="research-figure rho-ladder-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" mobile="/assets/portfolio-optimization/rho-ladder_mobile" alt="Four panels showing risk calibration, holding-period beta error, annual turnover, and net Sharpe across correlation shrinkage for the optimizer with and without trading controls, with the 0.3 to 0.6 region shaded" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 1: Correlation shrinkage.</strong> Risk calibration (including the volatility multiplier), mean holding-period beta error, annual turnover and net Sharpe at each shrinkage value, development period. The shaded band marks 0.3–0.6; the selected value is 0.5.</p>

[TBD: how calibration, beta error, turnover and Sharpe move from 0.3 to 0.6,
and at zero and full shrinkage.] Full shrinkage also separates the two sources
of the optimizer's gain: at $$\rho=1$$ it keeps [TBD] of its gross-return gain
over score-weighted volatility scaling, so [TBD: how much comes from
correlations and how much from the limits and score scaling].

Factor models are the other standard route to a covariance matrix, and they
combine with shrinkage in the same optimizer. I stick with empirical
correlations here. For an introduction I liked HRT's
[*Modeling Equities Returns: The Linear Case*](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/)
and Chapter 4 of Giuseppe Paleologo's
[*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6).

## Portfolio limits

In the regression article, volatility scaling runs 35–50% net long through
2021 with market beta near 0.1, because the calmer long side gets larger
positions. The limits in $$\mathcal W_t$$ are there to stop that and a few
other failures:

- Gross exposure (200%) stops the optimizer from levering up low-risk
  combinations to reach the volatility target.
- Estimated beta (±0.05) limits market exposure at each rebalance. I limit
  beta rather than forcing dollar neutrality because the long book has the
  lower beta; net exposure (±25%) caps how far the portfolio can run net long
  to balance it.
- The name limit (4%) caps the damage from one bad forecast or one
  underestimated volatility.
- Sector limits (±20% net, 30% of either book) matter because the Ridge
  target is ranked within sectors: a sector tilt would be a bet the ranking
  was never trained to make.

Long candidates can take positive or zero weights and short candidates
negative or zero weights, so the optimizer sizes the selected names but
cannot flip their side. The limits apply to target weights; the appendix
covers how holdings drift between rebalances.

## Step by step
{: #development-results }

Table 1 builds from the regression article's rule to the final portfolio,
one change at a time, with the same Ridge ranking throughout. The first row
is that article's rule: equal signal weights within each book, scaled by
volatility.[^row-one] The second gives stronger scores larger signal weights.
The third sizes the stocks jointly. The fourth adds two trading controls,
explained in the next section: a rank buffer that keeps existing holdings
eligible, and a penalty on trading.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: From volatility scaling to joint sizing.</strong> Development period, September 1998–December 2021. Means of metrics calculated separately for the three schedules, with min–max Sharpe in parentheses. Returns are geometric and annualized; Sharpe uses the arithmetic mean daily return and a zero risk-free rate; turnover is two-way and annualized, relative to strategy capital. Net results charge 5 bp per dollar traded.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max drawdown</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Optimizer</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

Weighting by score takes Sharpe from [TBD] to [TBD]. Joint sizing adds
[TBD] points of gross return and lifts Sharpe to [TBD], but turnover rises
from [TBD]× to [TBD]× a year. The trading controls keep [TBD] of that gross
return and bring turnover down to [TBD]×, for a Sharpe of [TBD].

Several things change at once between the second and third rows: the
optimizer uses correlations, 21-session instead of 60-session volatility and
the volatility multiplier; the score enters linearly instead of through
logistic signal weights; and the volatility target and the gross, net, beta
and sector limits apply. The third row compares the full rule rather than
isolating each change.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" mobile="/assets/portfolio-optimization/performance-and-drawdowns_mobile" alt="Development-period net growth and drawdowns for volatility scaling and the optimizer with trading controls" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 2: Development-period growth and drawdowns.</strong> Net growth index (log scale) and drawdown after trading costs for the first and last rules in Table 1, September 1998–December 2021. Each path averages three separately compounded schedules. The rules run at different volatilities; Table 1 compares Sharpe.</p>

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

under the same constraints and risk budget. Ignoring risk and limits, moving
weight from an existing holding to a new name pays only if the new name's
sizing score beats the old one's by more than $$2c$$ per unit of weight
moved. An L1 penalty creates this kind of no-trade zone, which suits linear
costs; a quadratic penalty would suit market impact. Because the penalty is
in score units, multiplying all scores by $$a$$ is the same as dividing
$$c$$ by $$a$$, so $$c=2.5\times10^{-4}$$ only means something relative to
these scores. The 5 bp cost is charged separately on executed trades.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: What each trading control contributes.</strong> Development period, September 1998–December 2021. Conventions as in Table 1.</caption>
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annual turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Neither control</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="selected-rule"><th scope="row">Buffer + penalty</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: turnover saved by each control alone and together; say the controls
work together only if the combined saving exceeds the sum.]

Figure 3 varies one control at a time around the chosen settings.

<div class="research-figure parameter-sensitivity-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" mobile="/assets/portfolio-optimization/parameter-sensitivity_mobile" alt="Development-period net Sharpe and annualized turnover across trade coefficients and rank-buffer cutoffs" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 3: Sensitivity to the trading controls.</strong> Development-period net Sharpe and annual turnover across trade coefficients <i>c</i> (×10<sup>−4</sup>; 0 means no penalty) and rank-buffer cutoffs (75 means no buffer). Points are schedule means; whiskers span the three schedules. Chosen settings are highlighted.</p>

[TBD: the coefficient plateau and the choice of 2.5; rank cutoffs 150–200 and
the choice of 175.]

## After 2021

Table 3 covers January 2022–May 2026, about four and a half years.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: The same rules after 2021.</strong> January 2022–May 2026. Conventions as in Table 1.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max drawdown</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Optimizer</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]<br><small>([TBD])</small></td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: how the four rules compare after 2021, with a paired block-bootstrap
interval for the Sharpe difference between the optimizer with trading controls
and volatility scaling.] Risk calibration, which the
multiplier sets close to one in development, is [TBD] after 2021.

The average hides a large spread across rebalance schedules. With trading
controls, net return differs by [TBD] points between the best and worst
schedule, against [TBD] for score-weighted volatility scaling. Trading more
slowly still helps on average, but much less consistently than in
development.

Much of the weakness comes from the short book in December 2022–February
2023. For the three schedules combined, the long book contributes about
[TBD] P&L points and the short book [TBD], where a P&L point is 1% of strategy
capital, summed over daily after-cost contributions. The
[attribution series](/quants/portfolio-attribution.html) looks at why short
books struggle in rebounds.

## Forecast beta versus realized beta

The beta limit applies to an estimate at each rebalance. Figure 4 tracks
the beta of the portfolio's realized returns over a trailing year, which
reflects holdings and market moves throughout that year.

<div class="research-figure risk-beta-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" mobile="/assets/portfolio-optimization/risk-calibration-and-beta_mobile" alt="Trailing 252-session realized market beta for volatility scaling and the optimizer with trading controls" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4: Realized beta.</strong> Month-end trailing 252-session market beta, averaged across the three schedules, from September 1999 after the return-window warm-up. The pale band marks the ±0.05 limit on estimated beta.</p>

Realized beta averages [TBD] for volatility scaling and [TBD] for the
optimizer with trading controls, and several episodes last for months and
reach [TBD]. I tried a shorter estimate: a 63-session [TBD: which window]
window removes the long episodes, but costs [TBD] points of net return a
year, more than the 0.5 points I was willing to give up. So I keep the
756-session estimate (appendix).

## What joint sizing buys, and what it costs

In development, joint sizing with trading controls lifts Sharpe from [TBD]
for the regression article's rule to [TBD], and maximum drawdown goes from
[TBD] to [TBD]. [TBD: which step contributes most.]

The cost is complexity and, without controls, turnover. The optimizer needs a
covariance estimate, a shrinkage choice, a risk multiplier and a set of
limits, and on its own it trades [TBD]× capital a year against [TBD]× for
volatility scaling. [TBD: whether the controls remove all of the extra
trading.] It also runs at [TBD] average gross against [TBD] for volatility
scaling, so the borrow, financing and impact costs left out here weigh more
on it. Its advantage over volatility scaling disappears at about [TBD] bp per
dollar traded.

Two problems remain. Realized beta drifts away from the rebalance-time
estimate for months at a time, and after 2021 the result depends heavily on
which week the portfolio rebalances.

## Appendix

### Allocation settings

<table class="research-table settings-table">
  <caption><strong>Table 4: Allocation settings.</strong></caption>
  <thead><tr><th>Component</th><th>Setting</th></tr></thead>
  <tbody>
    <tr><th scope="row">Selection</th><td>75 long + 75 short; with the buffer, existing holdings stay eligible through rank 175</td></tr>
    <tr><th scope="row">Volatility-scaled rules</th><td>Equal or logistic (slope 2) signal weights; 60-session volatility, 20% reference and 5% floor; 4% name cap; each book scaled down above 100% gross</td></tr>
    <tr><th scope="row">Joint portfolio limits</th><td>7% forecast volatility; 200% gross; 4% per name; ±25% net; ±0.05 estimated beta</td></tr>
    <tr><th scope="row">Sector limits</th><td>±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Covariance estimate</th><td>21-session volatility; 756-session correlations of volatility-standardized returns (252 observations minimum); 50% shrinkage toward identity; volatility multiplier [TBD], estimated on development data</td></tr>
    <tr><th scope="row">Beta estimate</th><td>756-session correlation with the market (252 observations minimum) combined with 21-session stock and market volatility</td></tr>
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

[TBD: the 63-session test in full: which window changes, the beta-error
results and the net-return cost with trading controls.]

[^calibration]: A different multiplier also changes the weights, including which constraints bind and how much the portfolio trades, so every result here uses the recalibrated forecasts.
[^row-one]: The regression article reports arithmetic annualized returns; here they are geometric, so net returns differ slightly while Sharpe and turnover are comparable.
