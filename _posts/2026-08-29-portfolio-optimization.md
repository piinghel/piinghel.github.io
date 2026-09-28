---
layout: post
title: "From Volatility Scaling to Joint Sizing"
description: "Sizing stocks together under a risk budget, then slowing the trading down with a rank buffer and a trade penalty."
date: 2026-08-29
last_modified_at: 2026-09-28
categories: ["Portfolio construction"]
article_label: Portfolio construction · Joint sizing
permalink: /quants/2026/08/29/portfolio-optimization.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/portfolio-optimization-study
---

In the articles on [low-volatility sizing](/quant/2024/12/15/low-volatility-factor.html)
and [regression](/quants/2025/02/09/multiple-linear-regression.html),
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
financing and market impact. I report September 1998–December 2021, the
development period, and January 2022–May 2026, the later period, separately.

## Sizing under a volatility budget

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

I don't have calibrated expected returns. The Ridge target is a sector-ranked
forward Sharpe ratio, so I multiply each prediction $$s_{i,t}$$ by the stock's
estimated daily volatility $$\widehat\sigma_{i,t}$$ to get a return-like
*sizing score* $$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$. With signed weights $$w_t$$, I solve

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

The inverse divides each component by its estimated variance, so the
optimizer puts its largest bets in the directions with the smallest estimated
variance, which is exactly where an underestimate does most damage. Shrinkage
pulls the eigenvalues toward their average of one, giving up some apparent
diversification for weights that are less sensitive to estimation error.

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
and realized risk agree. I set the multiplier to 1.55, where development
calibration is 1.01.

Figure 1 runs the final portfolio, the optimizer with the trading controls
described below, at five shrinkage values in development.

<div class="research-figure rho-ladder-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" mobile="/assets/portfolio-optimization/rho-ladder_mobile" alt="Four panels showing risk calibration, beta bias, annual turnover and net Sharpe across correlation shrinkage for the optimizer with trading controls" version="16" %}
</div>

<p class="figure-caption"><strong>Figure 1: Correlation shrinkage.</strong> The optimizer with trading controls at five shrinkage values, development period: risk calibration, beta bias (realized minus forecast beta over the next holding period), annual turnover and net Sharpe. The chosen 0.5 is highlighted.</p>

From 0.25 to 0.5, calibration stays close to one and Sharpe near 1.33.
Without shrinkage realized risk runs 11% above forecast and turnover rises
from 23× to 26×. With correlations removed entirely, realized risk runs 50%
above forecast and Sharpe falls to 1.05. Realized beta also runs about 0.06 above forecast at every
setting up to 0.75, a bias I come back to below.

## Portfolio limits

In the regression article, volatility scaling runs 35–50% net long through
2021 with market beta near 0.1, because the lower-volatility long book gets larger
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
their side.[^drift] Table 1 lists all settings.

<table class="research-table settings-table">
  <caption><strong>Table 1: Allocation settings.</strong></caption>
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

## One change at a time
{: #development-results }

Table 2 builds from the regression article's rule to the final portfolio,
one change at a time, with the same Ridge ranking throughout. The first row
is that article's rule: equal signal weights within each book, scaled by
volatility. The second gives stronger scores larger signal weights.
The third sizes the stocks jointly. The fourth adds two trading controls,
explained in the next section: a rank buffer that keeps existing holdings
eligible, and a penalty on trading.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 2: From volatility scaling to joint sizing.</strong> Development period, September 1998–December 2021. Means of metrics calculated separately for the three schedules, with min–max Sharpe in parentheses. Returns are geometric and annualized; Sharpe uses the arithmetic mean daily return and a zero risk-free rate; turnover is two-way and annualized, relative to strategy capital. Net results charge 5 bp per dollar traded.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max drawdown</th><th>Two-way turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>9.42%</td><td>7.88%</td><td>8.05%</td><td>0.98<br><small>(0.89–1.16)</small></td><td>−19.8%</td><td>28.4×</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>10.58%</td><td>8.95%</td><td>8.68%</td><td>1.03<br><small>(0.96–1.17)</small></td><td>−21.6%</td><td>29.7×</td></tr>
    <tr><th scope="row">Optimizer</th><td>11.02%</td><td>9.03%</td><td>7.07%</td><td>1.26<br><small>(1.22–1.29)</small></td><td>−15.2%</td><td>36.1×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>10.65%</td><td>9.40%</td><td>7.01%</td><td>1.32<br><small>(1.26–1.36)</small></td><td>−15.5%</td><td>22.6×</td></tr>
  </tbody>
</table>

Weighting by score takes Sharpe from 0.98 to 1.03. Joint sizing adds less
than half a point of gross return, but it does so at 7.1% volatility instead
of 8.7%, which lifts Sharpe to 1.26; the maximum drawdown falls from about
22% to 15%, partly because the book runs smaller. It also raises turnover from 30× to 36× a year. The trading
controls keep almost all of the gross return and bring turnover down to
23×, below either volatility-scaled rule, for a Sharpe of **1.32**.

Several things change at once between the second and third rows:
correlations, 21-session instead of 60-session volatility, the volatility
multiplier, a linear instead of logistic score, the volatility target and the
limits. The full-shrinkage point in Figure 1 keeps all of these, plus the
trading controls, and drops only the correlations. Its Sharpe of 1.05 is level
with the score-weighted rule's 1.03, so the gain comes from the correlations.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" mobile="/assets/portfolio-optimization/performance-and-drawdowns_mobile" alt="Development-period net growth and drawdowns for volatility scaling and the optimizer with trading controls" version="16" %}
</div>

<p class="figure-caption"><strong>Figure 2: Development-period growth and drawdowns.</strong> Net growth index (log scale) and drawdown after trading costs for the first and last rules in Table 2, September 1998–December 2021. Each path averages three separately compounded schedules, so its drawdowns are shallower than the per-schedule maxima in Table 2. The rules run at different volatilities; Table 2 compares Sharpe.</p>

The lead builds steadily: scaled to the same volatility, no single year
supplies more than about a sixth of it, and 1999–2000 together about a fifth.
It shows most in the two large drawdowns, about 13% against 18% in 2008–09 and
14% against 18% in 2020–21.

## Trading controls

At each rebalance, the optimizer without controls starts from the newly selected
stocks. A small change in rank or covariance can trigger a replacement whose
benefit is smaller than its cost.

Take a long stock whose rank slips from 60 to 110. The optimizer without controls drops
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
moved. The penalty is in score units, not a cost estimate; the 5 bp cost is
charged separately on executed trades.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 3: What each trading control contributes.</strong> Development period, September 1998–December 2021. Conventions as in Table 2.</caption>
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Two-way turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Optimizer, no controls</th><td>11.02%</td><td>9.03%</td><td>1.26</td><td>36.1×</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>11.29%</td><td>9.48%</td><td>1.31</td><td>32.9×</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>10.80%</td><td>9.19%</td><td>1.30</td><td>29.4×</td></tr>
    <tr class="selected-rule"><th scope="row">Both (final rule)</th><td>10.65%</td><td>9.40%</td><td>1.32</td><td>22.6×</td></tr>
  </tbody>
</table>

The buffer alone cuts turnover by about 3× capital a year and the penalty
alone by about 7×; together they cut it by 13.5×, more than the sum of the two. The buffer
keeps more holdings eligible, and the penalty makes keeping them the default.

Figure 3 varies one control at a time around the chosen settings.

<div class="research-figure parameter-sensitivity-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" mobile="/assets/portfolio-optimization/parameter-sensitivity_mobile" alt="Development-period net Sharpe and annualized turnover across trade coefficients and rank-buffer cutoffs" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 3: Sensitivity to the trading controls.</strong> Development-period net Sharpe and annual turnover across trade coefficients <i>c</i> (×10<sup>−4</sup>; 0 means no penalty) and rank-buffer cutoffs (75 means no buffer). Points are schedule means; whiskers span the three schedules. Chosen settings are highlighted.</p>

Net Sharpe barely moves: 1.29–1.33 across trade coefficients from 0 to 5
and 1.30–1.32 across cutoffs from 75 to 225, while turnover falls from 33× to
19× and from 29× to 21×. The settings I use, 2.5 and 175, sit inside both
plateaus. A larger coefficient or cutoff would cut turnover further at little
cost in Sharpe; I keep the earlier settings rather than tune them on this run.

## After 2021

Table 4 covers January 2022–May 2026, about four and a half years.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 4: The same rules after 2021.</strong> January 2022–May 2026. Conventions as in Table 2.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max drawdown</th><th>Two-way turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>8.43%</td><td>7.12%</td><td>10.16%</td><td>0.73<br><small>(0.67–0.83)</small></td><td>−9.4%</td><td>24.3×</td></tr>
    <tr><th scope="row">Volatility-scaled, score-weighted</th><td>8.62%</td><td>7.19%</td><td>11.00%</td><td>0.69<br><small>(0.63–0.73)</small></td><td>−10.4%</td><td>26.4×</td></tr>
    <tr><th scope="row">Optimizer</th><td>6.55%</td><td>5.12%</td><td>7.44%</td><td>0.71<br><small>(0.44–0.84)</small></td><td>−8.0%</td><td>26.9×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>7.16%</td><td>6.37%</td><td>7.46%</td><td>0.87<br><small>(0.68–0.96)</small></td><td>−7.3%</td><td>14.7×</td></tr>
  </tbody>
</table>

All four rules earn less than in development. The optimizer on its own no
longer beats volatility scaling. With the trading controls it has the higher
Sharpe, 0.87 against 0.73, but the lower net return, 6.4% against 7.1%,
because it runs at 7.5% volatility instead of 10.2%. It also has the smaller
drawdown and about 60% of the turnover. The Sharpe difference is not firm: a
paired block bootstrap of the combined schedules puts its 95% interval at −0.34 to +0.65.[^bootstrap] Risk
calibration after 2021 is 1.06, so the portfolio runs about 6% above its
forecast.

The lead also depends on the schedule: net Sharpe is 0.96 against 0.68 and
0.96 against 0.83 on two of them, but 0.68 against 0.67 on the third.

Its worst stretch is the market rebound of December 2022–February 2023, a
7.3% drawdown for the three schedules combined: the long book made about 3.3%
of fixed strategy notional and the short book lost 10.8%.

## Forecast beta versus realized beta

The beta limit applies to an estimate at each rebalance. Figure 4 tracks
the beta of the portfolio's realized returns over a trailing year, which
reflects holdings and market moves throughout that year.

<div class="research-figure risk-beta-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" mobile="/assets/portfolio-optimization/risk-calibration-and-beta_mobile" alt="Trailing 252-session realized market beta for volatility scaling and the optimizer with trading controls, with the plus or minus 0.05 limit band" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 4: Realized beta.</strong> Month-end trailing 252-session market beta, averaged across the three schedules, from September 1999 after the return-window warm-up. The pale band marks the optimizer's ±0.05 limit, which applies to its rebalance-time estimate.</p>

Over the full development period, realized beta is 0.10 for volatility
scaling and 0.08 for the optimizer with trading controls; after 2021 it is
0.07 and 0.02. The trailing-year beta is less comfortable: in development
the optimizer's sits above the +0.05 limit at 77% of month-ends (38% after
2021), peaks near 0.3 and tracks volatility scaling closely. It is the bias from Figure 1: the rebalance-time
estimate understates the portfolio's beta by about 0.06.

## Joint sizing pays once trading is controlled

In development, joint sizing with trading controls raises net return from
7.9% to 9.4% while cutting volatility from about 8% to 7%, so Sharpe rises
from 0.98 for the regression article's rule to 1.32. Most of that comes from
the correlations: shrink them away and Sharpe falls back to 1.05.

The cost is complexity and, without controls, turnover. The optimizer needs a
covariance estimate, a shrinkage choice, a risk multiplier and a set of
limits, and on its own it trades 36× capital a year against 28× for
volatility scaling; at about 22 bp per dollar traded its advantage would be
gone. The trading controls remove that problem: the portfolio then trades
less than volatility scaling, so higher costs widen its lead. It does run at
about 160% average gross against 138% in development, so the borrow,
financing and impact costs left out here weigh more on it.

The [attribution series](/quants/portfolio-attribution.html) breaks this
portfolio's P&L down by the ranking's themes.

Two weaknesses remain: realized beta runs above the rebalance-time estimate
for months at a time, and after 2021 the advantage is small relative to its
uncertainty and depends on the rebalance schedule. Neither weakness changes my
verdict: joint sizing with trading controls earns more per
unit of risk than volatility scaling in both periods, by a clear margin in
development and an unproven one after 2021, and it trades less.

## References

Lasse Heje Pedersen, Abhilash Babu and Ari Levine,
[*Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543),
*Financial Analysts Journal*, 2021, pp. 129–130.

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapter 4 on multi-factor models, the other standard route to a
covariance matrix.

Hudson River Trading, [*Modeling Equities Returns: The Linear Case*](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/),
a clear introduction to factor risk models.

[^correlation-repair]: Before estimating correlations I cap daily returns at ±30% and set pairs with too little overlapping history to 0.50; negative eigenvalues of the result are clipped to zero.
[^drift]: All limits apply to target weights. After next-close execution and later price moves, holdings can drift outside them until the next rebalance; the trade penalty measures changes from these drifted weights.
[^bootstrap]: I resample the daily net returns of each rule's three schedules combined, 5,000 times in 21-session blocks shared by both rules. The combined schedules differ in Sharpe by 0.15, against 0.14 for the schedule means in Table 4.
