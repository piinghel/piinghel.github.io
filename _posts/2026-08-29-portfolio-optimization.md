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
of the portfolio open. Portfolio limits break that separation: scaling from
5% to 7% forecast volatility turns a 4% position into 5.6% and breaches the
name cap. So I put the volatility budget inside the optimization.

My inputs are relative scores, not calibrated expected returns. For each
stock I multiply its Ridge prediction $$s_{i,t}$$ by its estimated daily
volatility $$\widehat\sigma_{i,t}$$ to get a *sizing score*
$$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$, which puts the scores back on each
stock's risk scale. With signed weights $$w_t$$, I solve

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq \sigma_{\mathrm{target}}^2,\\
& w_t\in\mathcal W_t,
\end{aligned}
$$

where $$\Sigma_t$$ is the annualized forecast covariance matrix,
$$\sigma_{\mathrm{target}}$$ is 7%, and $$\mathcal W_t$$ holds the portfolio
limits below.

## Covariance and correlation shrinkage
{: #covariance-and-risk-forecasts }

The optimizer is only as good as $$\Sigma_t$$. I let each stock's volatility
react faster than the correlations: 21-session volatility, 756-session
correlations of volatility-standardized returns.[^correlation-repair] I then
shrink the correlation estimate $$\widetilde R_t$$ toward the identity matrix:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I.
$$

At $$\rho=0$$ I keep the estimated correlations; at $$\rho=1$$ I discard
them. I use $$\rho=0.5$$, which halves every off-diagonal correlation and
leaves each stock's own variance unchanged.

I like the explanation of why this helps in Pedersen, Babu and Levine's
*Enhanced Portfolio Optimization*, through principal components. Each
component is a combination of volatility-standardized returns with
unit-length eigenvector $$q_j$$ and estimated variance $$\lambda_j$$.
Shrinkage keeps the eigenvectors and gives

$$
\begin{aligned}
\lambda_j(\rho)&=(1-\rho)\lambda_j+\rho,\\
C(\rho)^{-1}q_j&=\frac{q_j}{\lambda_j(\rho)}.
\end{aligned}
$$

The eigenvalues move toward their average of one. Because the inverse divides
each component by its estimated variance, a favorable score in a
low-variance direction attracts a large allocation, and an underestimated
variance amplifies the error in that score too. Shrinking gives up some of the
most attractive-looking diversification for weights that are less sensitive
to estimation error.

The covariance matrix and its inverse, the *precision matrix*, are

$$
\begin{aligned}
\Sigma_t&=D_tC_t(\rho)D_t,\\
\Sigma_t^{-1}&=D_t^{-1}C_t(\rho)^{-1}D_t^{-1},
\end{aligned}
$$

with $$D_t$$ the diagonal matrix of annualized volatility forecasts. At full
shrinkage, the sizing scores cancel one volatility factor and the weights
become proportional to $$s_{i,t}/\widehat\sigma_{i,t}$$: volatility scaling
again, apart from the portfolio limits. Joint sizing is the same idea with
correlations added back in.

An optimized portfolio tends to under-forecast its own risk, because the
optimizer seeks out the directions whose estimated risk is lowest. Halving
the correlations also halves their average, so the model understates common
risk as well. I correct both with a multiplier on the volatility forecasts in
$$D_t$$. *Risk calibration* is the square root of mean realized
holding-period variance divided by mean forecast variance; one means forecast
and realized risk agree. With the multiplier I used before, 1.18, the
optimizer forecasts 7% but realizes 8.5–9.0% in development, a calibration of
about 1.25. Scaling the multiplier by that ratio doesn't quite close the
gap, because the limits change the weights as well, so I adjust it once more
and settle on 1.55, where development calibration is 1.01. The later period is the
real test (Table 3).

Figure 1 shows why I keep some estimated correlation. I rebuild the
optimizer at each shrinkage value using development data, with and without
the trading controls described below.

<div class="research-figure rho-ladder-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" mobile="/assets/portfolio-optimization/rho-ladder_mobile" alt="Four panels showing risk calibration, holding-period beta error, annual turnover, and net Sharpe across correlation shrinkage for the optimizer with and without trading controls, with the 0.3 to 0.6 region shaded" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 1: Correlation shrinkage.</strong> Risk calibration, mean holding-period beta error, annual turnover and net Sharpe at each shrinkage value, development period. The shaded band marks 0.3–0.6; the selected value is 0.5.</p>

[TBD: how the four measures move from 0.3 to 0.6 and at the extremes. At
$$\rho=1$$, the share of the optimizer's gross-return gain over score-weighted
volatility scaling that survives, which separates the gain from correlations
from the gain from the limits.]

## Portfolio limits

In the regression article, volatility scaling runs 35–50% net long through
2021 with market beta near 0.1, because the calmer long side gets larger
positions. The limits in $$\mathcal W_t$$ stop that and a few other failures:

- Gross exposure (200%) stops the optimizer from levering up low-risk
  combinations to reach the volatility target.
- Estimated beta (±0.05) limits market exposure at each rebalance. Because
  the long book has the lower beta, I limit beta rather than dollars and cap
  net exposure at ±25%.
- The name limit (4%) caps the damage from one bad forecast or one
  underestimated volatility.
- Sector limits (±20% net, 30% of either book) matter because the Ridge
  target is ranked within sectors: a sector tilt would be a bet the ranking
  was never trained to make.

Long candidates take positive or zero weights and short candidates negative
or zero weights, so the optimizer sizes the selected names but cannot flip
their side.[^drift] Table 4 lists all settings.

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
    <tr><th scope="row">Volatility-scaled</th><td>9.42%</td><td>7.88%</td><td>8.05%</td><td>0.98<br><small>(0.89–1.16)</small></td><td>−19.8%</td><td>28.4×</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>10.57%</td><td>8.95%</td><td>8.68%</td><td>1.03<br><small>(0.96–1.17)</small></td><td>−21.6%</td><td>29.7×</td></tr>
    <tr><th scope="row">Optimizer</th><td>11.02%</td><td>9.03%</td><td>7.06%</td><td>1.26<br><small>(1.22–1.29)</small></td><td>−15.2%</td><td>36.1×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>10.65%</td><td>9.40%</td><td>7.01%</td><td>1.32<br><small>(1.26–1.36)</small></td><td>−15.5%</td><td>22.6×</td></tr>
  </tbody>
</table>

Weighting by score takes Sharpe from 0.98 to 1.03. Joint sizing adds less
than half a point of gross return, but it does so at 7.1% volatility instead
of 8.7%, which lifts Sharpe to 1.26 and cuts the maximum drawdown from about
22% to 15%. It also raises turnover from 30× to 36× a year. The trading
controls keep almost all of the gross return and bring turnover down to
23×, below either volatility-scaled rule, for a Sharpe of **1.32**.

Several things change at once between the second and third rows: the
optimizer uses correlations, 21-session instead of 60-session volatility and
the volatility multiplier; the score enters linearly instead of through
logistic signal weights; and the volatility target and the limits apply.

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

The buffer only keeps a holding eligible; a trade penalty makes keeping it
the default. With $$w_t^{\mathrm{pre}}$$ the weights just before rebalancing
and *trade coefficient* $$c$$, the objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

under the same constraints and risk budget. Ignoring risk and limits, moving
weight from an existing holding to a new name pays only if the new name's
sizing score beats the old one's by more than $$2c$$ per unit of weight
moved. The penalty is in score units, so $$c=2.5\times10^{-4}$$ only means
something relative to these scores. The 5 bp cost is charged separately on
executed trades.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: What each trading control contributes.</strong> Development period, September 1998–December 2021. Conventions as in Table 1.</caption>
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annual turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Neither control</th><td>11.02%</td><td>9.03%</td><td>1.26</td><td>36.1×</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>11.29%</td><td>9.48%</td><td>1.31</td><td>32.9×</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>10.80%</td><td>9.19%</td><td>1.30</td><td>29.4×</td></tr>
    <tr class="selected-rule"><th scope="row">Buffer + penalty</th><td>10.65%</td><td>9.40%</td><td>1.32</td><td>22.6×</td></tr>
  </tbody>
</table>

The buffer alone saves about 3 times capital a year and the penalty alone
about 7; together they save 13.5, more than the two separately. The buffer
keeps more holdings eligible, and the penalty makes keeping them the default.

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
    <tr><th scope="row">Volatility-scaled</th><td>8.43%</td><td>7.11%</td><td>10.16%</td><td>0.73<br><small>(0.67–0.83)</small></td><td>−9.4%</td><td>24.3×</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>8.62%</td><td>7.19%</td><td>11.00%</td><td>0.68<br><small>(0.63–0.73)</small></td><td>−10.4%</td><td>26.4×</td></tr>
    <tr><th scope="row">Optimizer</th><td>6.55%</td><td>5.12%</td><td>7.44%</td><td>0.70<br><small>(0.44–0.84)</small></td><td>−8.0%</td><td>26.9×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>7.16%</td><td>6.37%</td><td>7.46%</td><td>0.87<br><small>(0.68–0.96)</small></td><td>−7.3%</td><td>14.7×</td></tr>
  </tbody>
</table>

All four rules earn less than in development. The optimizer on its own no
longer beats volatility scaling; with the trading controls it does, 0.87
against 0.73, at lower volatility, a smaller drawdown and about 60% of the
turnover. That difference is not firm: a paired block bootstrap of the
combined books puts its 95% interval at −0.34 to +0.65.[^bootstrap] Risk
calibration after 2021 is 1.06, so the portfolio runs about 6% above its
forecast.

The average also hides a spread across rebalance schedules. With trading
controls, net return differs by 2.3 points between the best and worst
schedule, against 1.8 for volatility scaling.

The worst stretch is the rebound of December 2022–February 2023. For the
three schedules combined, the long book contributes about +3.3 P&L points and
the short book −10.8, where a P&L point is 1% of strategy capital, summed over
daily after-cost contributions.

## Forecast beta versus realized beta

The beta limit applies to an estimate at each rebalance. Figure 4 tracks
the beta of the portfolio's realized returns over a trailing year, which
reflects holdings and market moves throughout that year.

<div class="research-figure risk-beta-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" mobile="/assets/portfolio-optimization/risk-calibration-and-beta_mobile" alt="Trailing 252-session realized market beta for volatility scaling and the optimizer with trading controls" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4: Realized beta.</strong> Month-end trailing 252-session market beta, averaged across the three schedules, from September 1999 after the return-window warm-up. The pale band marks the ±0.05 limit on estimated beta.</p>

Over the full development period, realized beta is 0.10 for volatility
scaling and 0.08 for the optimizer with trading controls; after 2021 it is
0.07 and 0.02. The trailing-year beta is less well behaved: several episodes
last for months and reach [TBD]. A 63-session [TBD: which window] window removes the long
episodes but costs [TBD] points of net return a year, more than the 0.5 points
I was willing to give up, so I keep the 756-session estimate.

## What joint sizing buys, and what it costs

In development, joint sizing with trading controls lifts Sharpe from 0.98
for the regression article's rule to 1.32 and shrinks the maximum drawdown
from about 20% to 15%. Most of that comes from sizing the stocks jointly: it
delivers the same return with less risk.

The cost is complexity and, without controls, turnover. The optimizer needs a
covariance estimate, a shrinkage choice, a risk multiplier and a set of
limits, and on its own it trades 36× capital a year against 28× for
volatility scaling; at about 22 bp per dollar traded its advantage would be
gone. The trading controls remove that problem: the portfolio then trades
less than volatility scaling, so higher costs widen its lead. It does run at
about 160% average gross against 138% in development, so the borrow,
financing and impact costs left out here weigh more on it.

Two problems remain. Realized beta drifts away from the rebalance-time
estimate for months at a time, and after 2021 the advantage is small relative
to its uncertainty and depends on which week the portfolio rebalances. The
[attribution series](/quants/portfolio-attribution.html) takes this portfolio
as its starting point and breaks down its P&L, including the short book's
losses in rebounds.

<table class="research-table settings-table">
  <caption><strong>Table 4: Allocation settings.</strong></caption>
  <thead><tr><th>Component</th><th>Setting</th></tr></thead>
  <tbody>
    <tr><th scope="row">Selection</th><td>75 long + 75 short; with the buffer, existing holdings stay eligible through rank 175</td></tr>
    <tr><th scope="row">Volatility-scaled rules</th><td>Equal or logistic (slope 2) signal weights; 60-session volatility, 20% reference and 5% floor; 4% name cap; each book scaled down above 100% gross</td></tr>
    <tr><th scope="row">Joint portfolio limits</th><td>7% forecast volatility; 200% gross; 4% per name; ±25% net; ±0.05 estimated beta</td></tr>
    <tr><th scope="row">Sector limits</th><td>±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Covariance estimate</th><td>21-session volatility; 756-session correlations of volatility-standardized returns (252 observations minimum); 50% shrinkage toward identity; volatility multiplier 1.55, estimated on development data</td></tr>
    <tr><th scope="row">Beta estimate</th><td>756-session correlation with the market (252 observations minimum) combined with 21-session stock and market volatility</td></tr>
    <tr><th scope="row">Trade penalty</th><td><i>c</i> = 2.5 × 10<sup>−4</sup> on the absolute change from drifted pre-trade weights</td></tr>
  </tbody>
</table>

## References

Lasse Heje Pedersen, Abhilash Babu and Ari Levine,
[*Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543),
*Financial Analysts Journal*, 2021, pp. 129–130.

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapter 4 on multi-factor models, the other standard route to a
covariance matrix.

Hudson River Trading, [*Modeling Equities Returns: The Linear Case*](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/),
a clear introduction to factor risk models.

[^correlation-repair]: Before estimating correlations I cap daily returns at ±30% and give pairs without enough overlapping history a correlation of 0.50. The matrix is then symmetrized, negative eigenvalues are clipped to zero and the unit diagonal is restored.
[^drift]: All limits apply to target weights. After next-close execution and later price moves, holdings can drift outside them until the next rebalance; the trade penalty measures changes from these drifted weights.
[^bootstrap]: Daily net returns of each rule's three schedules combined, resampled in shared 21-session blocks, 5,000 draws. The Sharpe difference of the combined books is 0.15, close to the 0.14 difference of the schedule means in Table 3.
[^row-one]: The regression article reports arithmetic annualized returns; here they are geometric, so net returns differ slightly while Sharpe and turnover are comparable.
