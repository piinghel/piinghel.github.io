---
layout: post
title: "Joint Sizing with Fewer Trades"
description: "Joint sizing adds turnover. A rank buffer and trade penalty recover more of the gross return."
date: 2026-08-29
last_modified_at: 2026-09-06
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
series_previous: /quants/2025/02/09/multiple-linear-regression.html
series_next: /quants/2026/09/05/risk-concentration.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/portfolio-optimization-study
---

<p class="article-summary">The joint allocation rule raises this Ridge portfolio's development-period Sharpe from 1.12 to 1.35, but adds turnover. Letting the optimizer keep acceptable holdings and penalizing replacements cuts turnover by about a third while preserving gross return. I use both controls, though the advantage is smaller and less consistent after 2021. Risk forecasts also understate realized volatility.</p>

A stock ranking tells me which names I prefer. It leaves another decision:
how much of each should I hold? Scaling by individual volatility is a useful
start, but several apparently modest positions can share the same risk.

I want to know whether sizing the stocks jointly makes better use of the
ranking, and whether that benefit survives trading costs. I compare joint
sizing with individual volatility scaling, then let the optimizer consider
what the portfolio already owns before replacing stocks.

## Three allocation rules

The comparison starts in September 1998, after the signals and risk estimates
have enough history. I choose settings using data through December 2021.
January 2022–May 2026 provides the later comparison, but that history has since
informed feature, allocation, and beta-estimator choices.

I use the Ridge ranking from the [preceding study](/quants/2025/02/09/multiple-linear-regression.html).
Every allocation rule starts from that same ranking and trades the same three
staggered schedules. A staggered schedule runs the full strategy
from a different starting week. Each schedule rebalances every three weeks,
uses the same next-close execution, and pays 5 basis points on traded notional.

- **Volatility-scaled** maps prediction scores to signal weights, scales each stock
  by its own volatility, and applies caps.
- **Optimizer** takes the same selected stocks and sizes them together under
  portfolio constraints.
- **Optimizer + trading controls** solves the same problem, but it may
  keep existing holdings from a wider rank range and penalizes changes in its
  objective.

This baseline differs from the regression article's allocation rule. There,
selected stocks start with equal signal weights before volatility scaling;
here, stronger prediction scores receive larger signal weights. The comparison
below therefore starts from a different Ridge portfolio.

The tables average metrics calculated separately for the three schedules. Returns are
geometric annualized returns; Sharpe uses arithmetic mean daily return and a
zero risk-free rate. Two-way turnover sums absolute executed trades relative
to strategy capital, annualized over the reporting window.

I change covariance, score scaling and constraints together when moving from
individual to joint sizing. This tests which complete rule I would use;
separating the benefit of covariance would need another comparison.

## Development results

The volatility-scaled rule is easy to inspect. But it sizes the long and short
books separately and never sees covariance. Several modest positions can
therefore carry the same market or sector risk without the rule recognizing the
overlap.

The optimizer sizes the selected stocks together under a forecast-risk budget,
with limits on gross and net exposure, individual names, market beta, and
sectors. Let $$w_t$$ be the signed portfolio weights. For each stock, I form
a sizing score $$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$ from its Ridge
prediction $$s_{i,t}$$ and estimated daily volatility
$$\widehat\sigma_{i,t}$$. These scores guide relative allocation; I have not
calibrated them as expected returns.

The regression target ranks forward returns divided by volatility. Multiplying
its prediction by stock volatility gives me a sizing convention on the stock's
risk scale, but ranking the target has already discarded return magnitudes.

The basic optimizer solves

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq 0.07^2,\\
& w_t\in\mathcal W_t.
\end{aligned}
$$

Here $$\Sigma_t$$ is the forecast covariance matrix on an annualized scale,
so $$w_t^\top\Sigma_t w_t$$ is annual portfolio variance. Its off-diagonal
terms capture how positions move together: each stock's risk depends on the
rest of the proposed portfolio. The set $$\mathcal W_t$$ imposes the remaining limits:
200% gross, ±25% net, 4% per name, ±0.05 estimated beta, and the sector caps
in Table 4. Long candidates can receive positive or zero weights; short
candidates negative or zero weights. The optimizer seeks the highest combined
score within these limits and the 7% forecast-risk budget.

These limits apply to target weights at a rebalance. Next-close execution and
subsequent price moves can take the actual holdings outside those bounds.

In Table 1, joint sizing adds about three and a half percentage points of gross
return at similar realized risk. It also trades 42.5 times capital annually,
versus 30.3 for volatility scaling. The third rule preserves almost all that
gross return while removing much of the extra trading.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: Joint sizing and trading costs.</strong> September 1998–December 2021, means of three schedule-level metrics. Returns are geometric and annualized; volatility is annualized. Net results charge 5 bp on traded notional. Drawdowns are reported as positive loss magnitudes.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Drawdown loss</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>10.58%</td><td>8.92%</td><td>7.92%</td><td>1.12</td><td>19.63%</td><td>30.3×</td></tr>
    <tr><th scope="row">Optimizer</th><td>14.00%</td><td>11.60%</td><td>8.41%</td><td>1.35</td><td>19.77%</td><td>42.5×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>13.91%</td><td>12.32%</td><td>8.40%</td><td>1.43</td><td>18.06%</td><td>28.2×</td></tr>
  </tbody>
</table>

Figure 1 gives the path behind the averages. The optimizer finishes above the
volatility-scaled rule. Adding the trading controls finishes highest and loses
less in its worst drawdown. Its lead opens mainly around 2000 and 2021 rather
than building at a steady rate. These are portfolios at their actual risk
levels: annualized volatility is 7.92% for volatility scaling, 8.41% for the
optimizer and 8.40% with trading controls. The higher paths therefore need to
be read alongside volatility and Sharpe in Table 1.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" mobile="/assets/portfolio-optimization/performance-and-drawdowns_mobile" alt="Development-period net growth and drawdowns for the volatility-scaled rule, optimizer, and optimizer with trading controls" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 1: Development-period results.</strong> Net growth index (log scale) and drawdown after trading costs, September 1998–December 2021. Paths average three separately compounded schedules and retain each rule's own risk level; cumulative performance alone is not a risk-adjusted comparison.</p>

## Keeping existing holdings

At each rebalance, the optimizer chooses weights for the newly selected stocks
without giving any credit for already owning them. A small change in
rank or covariance can then trigger a replacement whose benefit is smaller
than its trading cost. A slightly better portfolio on paper can be a worse
trade in practice.

The optimizer is doing what I asked: finding attractive weights for the stocks
it is allowed to hold. I have to give it both permission to keep an acceptable
holding and a reason to care about the trade required to replace it.

Take a long stock whose rank slips from 60 to 110. The optimizer drops it
because only the top 75 enter the new selection. The optimizer with trading
controls may retain it while it remains inside the wider top 175. It starts from
the existing weights after intervening price moves.

An incumbent outside the wider holding range must still close, and the
backtest charges for that exit. The penalty cannot keep an ineligible stock.

The sizing scores and risk budget stay the same. If
$$w_t^{\mathrm{pre}}$$ contains the weights just before rebalancing and
$$c$$ is the trade coefficient, the objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

under the same portfolio constraints. The wider holding range gives the
optimizer more incumbents to choose from. The second term makes every change
pay for moving away from the current weights. The trade coefficient controls
that reluctance.

The score scale matters once I add this penalty. Multiplying all sizing scores
by a positive constant leaves the basic optimizer's preferred weights unchanged.
With the penalty, multiplying scores by $$a$$ is equivalent to dividing $$c$$
by $$a$$. My choice of $$c=2.5\times10^{-4}$$ belongs to this score convention;
it is not a calibrated 2.5 bp trading cost.

The L1 term counts both sides of a replacement. Selling a 1% position and buying
another 1% position changes $$\lVert w_t-w_t^{\mathrm{pre}}\rVert_1$$ by 2%.
The optimizer keeps the incumbent unless the new score-and-risk combination
clears that hurdle. Constraints can still force a trade when the old position
no longer fits. I tune this coefficient to control how readily the optimizer
trades; the backtest separately charges 5 bp on executed trades.

Table 2 separates the two controls. A *rank buffer* lets an existing long
remain eligible down to rank 175, while new positions still enter through the
top 75; the short book uses the corresponding bottom ranks. The buffer alone
saves little turnover. With a penalty on changing weights, it becomes much
more useful: the optimizer can retain an acceptable incumbent instead of
paying to replace it.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: What the trading controls contribute.</strong> Development-period means across three schedules, September 1998–December 2021. Returns are geometric and annualized, with net results charging 5 bp per dollar traded. The buffer uses rank 175 and the penalty uses <i>c</i> = 2.5 × 10<sup>−4</sup>; other allocation settings are the same.</caption>
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annual turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Neither control</th><td>14.00%</td><td>11.60%</td><td>1.35</td><td>42.5×</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>14.07%</td><td>11.84%</td><td>1.37</td><td>39.5×</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>13.95%</td><td>11.95%</td><td>1.39</td><td>35.4×</td></tr>
    <tr class="selected-rule"><th scope="row">Buffer + penalty</th><td>13.91%</td><td>12.32%</td><td>1.43</td><td>28.2×</td></tr>
  </tbody>
</table>

The buffer saves about three times capital in annual trading without the
penalty, and seven times with it.
That is why I use the two controls together. They change which stocks remain
eligible and how much I hold, so the difference includes changes in positions
as well as trading costs.

Figure 2 checks nearby settings in development, varying one control at a time
around the chosen penalty and rank cutoff. The coefficient axis uses units of
$$10^{-4}$$; the plotted value 2.5 is the setting in Table 4.

<div class="research-figure parameter-sensitivity-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" mobile="/assets/portfolio-optimization/parameter-sensitivity_mobile" alt="Development-period net Sharpe and annualized turnover for six trade coefficients and five holding-rank cutoffs" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 2: A broad return–turnover trade-off.</strong> Development-period net Sharpe and annual turnover. Points are schedule means; whiskers in the Sharpe panels span the observed schedules. Each group varies one setting while holding the other fixed; the chosen settings are highlighted.</p>

From 1 through 3, net Sharpe stays between 1.42 and 1.43 while turnover keeps
falling, from 34× to 27×. I choose 2.5 for the lower turnover within that
plateau; pushing to 5 gives back some return.

Rank cutoffs from 150 to 200 also give similar Sharpe, with modest turnover
savings. I use 175: moving to 200 saves less than another turn and worsens
mean maximum drawdown.

A 5 bp charge on 28.2 times annual turnover costs about 1.41% of strategy capital
per year on an arithmetic basis. The gap between gross and net geometric
returns includes the effect of compounding as well as these daily charges.

## Results after 2021

Table 3 starts on the first trading day of 2022. All three rules weaken relative
to their development results. The optimizer trails volatility scaling after
trading more. The trading controls change the result: net return is 8.0% versus
7.4%, Sharpe is 0.87 versus 0.78, and turnover falls below the baseline.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: The allocation rules in later history.</strong> January 2022–May 2026, a later period revisited during research. Schedule averaging, geometric-return, drawdown, and cost conventions match Table 1.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Drawdown loss</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>8.92%</td><td>7.38%</td><td>9.73%</td><td>0.78</td><td>8.65%</td><td>28.4×</td></tr>
    <tr><th scope="row">Optimizer</th><td>8.63%</td><td>6.47%</td><td>9.39%</td><td>0.71</td><td>9.41%</td><td>40.0×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>9.33%</td><td>7.99%</td><td>9.32%</td><td>0.87</td><td>9.05%</td><td>24.6×</td></tr>
  </tbody>
</table>

The average hides a large calendar effect. The optimizer with trading controls has a
4.5-point spread in net return across the three schedules, compared with 1.5
points for the volatility-scaled rule. Two schedules favor the optimizer and
one is much weaker. Trading more slowly still helps on average, but the
result is much less consistent than during development.

The difficult December 2022–February 2023 episode also shows what the controls
leave unresolved. Across schedules, the long book contributes about +7.2
percentage points and the short book −16.4, measured as sums of daily
after-cost contributions. A market-only decomposition explains little of the
loss. That locates the problem in the short book, but identifying a shared
sector or style exposure requires a separate attribution study.

## Covariance and risk forecasts

The optimizer can only work with the risk estimate I give it. If a combination
of stocks looks unusually safe, it becomes an attractive place to put more
weight. That is useful when the estimate is right. When it is wrong, the
optimizer can put more capital behind the error.

I let individual volatility react faster than correlations, repair the
pairwise correlation estimate, and shrink it toward the identity matrix:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I.
$$

Here $$\widetilde R_t$$ is the repaired correlation estimate and $$I$$ has
ones on the diagonal and zeros elsewhere. At $$\rho=0$$ I retain the estimated
correlations; at $$\rho=1$$ I discard them. The implemented value,
$$\rho=0.5$$, halves the off-diagonal correlations while keeping each stock's
own variance.

In [*Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543),
Pedersen, Babu, and Levine (2021) explain why this can help. An optimizer can
take large positions in combinations with very low estimated risk, where
errors in both risk and expected return matter disproportionately. Correlation
shrinkage raises the smallest eigenvalues, reducing the attraction of these
apparently safe combinations. I use that shrinkage idea inside this constrained
allocation problem.

The shrunk correlation matrix becomes a covariance matrix through

$$
\Sigma_t=\kappa^2D_tC_t(\rho)D_t,
$$

where $$D_t$$ contains annualized stock-volatility estimates. Volatility uses
21 days and correlations use 756 days of volatility-standardized returns,
with 252 observations required. This lets the risk level respond without
re-estimating every stock relationship on a short window. The multiplier
$$\kappa=1.18$$ scales forecast volatility.

Before shrinkage, daily returns are capped at ±30% for correlation estimation.
Missing pairs use a 0.50 fallback. I symmetrize the pairwise matrix, clip
negative eigenvalues, and restore its unit diagonal. The fallback is not
uniformly conservative in a long–short portfolio: its effect depends on the
signs of the positions.

Figure 3 shows why I keep some estimated correlation. I rebuild both joint
rules at each shrinkage value using development data. From 0.3 to 0.6,
forecast calibration, beta error, turnover, and Sharpe move relatively little.
With no shrinkage, realized risk exceeds forecast by more. Full shrinkage
discards shared-risk information and misses by more again. The broad middle
matters more than the exact point inside it.

<div class="research-figure rho-ladder-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" mobile="/assets/portfolio-optimization/rho-ladder_mobile" alt="Four panels showing risk calibration, holding-period beta error, annual turnover, and net Sharpe across correlation shrinkage for both optimizers, with the 0.3 to 0.6 region shaded" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 3: A broad middle region for correlation shrinkage.</strong> Both joint rules are rebuilt at each shrinkage value on development data. The four panels show risk calibration, mean absolute holding-period beta error, annual two-way turnover, and net Sharpe. The shaded band marks 0.3–0.6; the implemented setting is 0.5. These historical comparisons informed the choice.</p>

Risk calibration takes the square root of mean realized holding-period
variance divided by mean variance forecast at execution. It uses complete
holding periods ending by December 2021; a ratio of one indicates agreement
in level. At the implemented shrinkage, realized volatility on this measure
is about 21% above forecast for the optimizer and 18% above for the version
with trading controls.

The full development results tell the same story: I asked for 7% forecast
volatility and got about 8.4% realized volatility. Shrinkage helps, but I still
need to recalibrate the risk level. I would estimate a new multiplier on
development data and rerun the portfolios. Changing covariance changes the
allocation decision too, including which constraints bind and how much I trade.

## Forecast beta versus realized beta

The beta limit also applies to an estimate at each rebalance. Figure 4 measures
something different: the beta of the portfolio's realized returns over a
trailing year. It reflects holdings and market moves throughout that year,
so it can remain far from zero even when new target weights satisfy the
point-in-time constraint.

<div class="research-figure risk-beta-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" mobile="/assets/portfolio-optimization/risk-calibration-and-beta_mobile" alt="Trailing 252-day realized market beta for the volatility-scaled rule and both optimizers during development" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4: Realized beta can persist after portfolio formation.</strong> Month-end trailing 252-day market beta, averaged across three schedules, September 1999–December 2021 after the return-window warm-up. The rebalance constraint uses a point-in-time estimate; the plotted beta measures the portfolio outcome over a trailing year.</p>

Joint sizing reduces the long departures from zero relative to volatility
scaling, but several episodes still last for months and reach roughly 0.2.
The holding-period diagnostics also show estimation error, beyond the effect
of a trailing measure remembering earlier positions. Both the measurement
window and the stock-beta estimate matter.

I tested a 63-day beta window in matched portfolios. It removes the flagged
persistent episodes, but with trading controls it does not improve the later
tail-error measure and loses 0.6 percentage points of annualized net return,
beyond the 0.5-point tolerance I used. I keep the existing estimate. That
rejection is also one reason the later period counts as reused research data.

## What joint sizing delivers

The useful result is the combination of joint sizing and a reason to keep
acceptable holdings. In development, the trading controls preserve almost all
of the optimizer's gross return while cutting turnover by about a third.
The wider rank range supplies alternatives; the penalty makes the optimizer
weigh their benefit against the cost of changing the book.

I keep both controls. The later comparison supports that choice on average,
but the advantage is smaller and depends more on the rebalance schedule.
Joint sizing therefore gives me a way to express portfolio limits and use the
ranking with less unnecessary trading. It still relies on imperfect risk
estimates and leaves substantial shared short-book risk to understand.

## Allocation settings

<table class="research-table settings-table">
  <caption><strong>Table 4: Allocation settings.</strong> The settings that determine selection, allocation and retention. Forecast variance is constrained jointly through the covariance matrix; long and short positions retain their respective signs.</caption>
  <thead><tr><th>Component</th><th>Setting</th></tr></thead>
  <tbody>
    <tr><th scope="row">Selection</th><td>75 long + 75 short; existing holdings eligible through rank 175 with the buffer</td></tr>
    <tr><th scope="row">Volatility-scaled baseline</th><td>Logistic signal shares with slope 2; 60-day volatility, 20% reference and 5% floor; 4% name cap; each book scales down above 100% gross</td></tr>
    <tr><th scope="row">Joint portfolio limits</th><td>7% forecast volatility; 200% gross; 4% per name; ±25% net; ±0.05 estimated beta</td></tr>
    <tr><th scope="row">Covariance estimate</th><td>21-day volatility; 756-day correlations of volatility-standardized returns (252 observations minimum); 50% shrinkage toward identity; volatility multiplied by 1.18</td></tr>
    <tr><th scope="row">Sector limits</th><td>±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Trading penalty</th><td><i>c</i> = 2.5 × 10<sup>−4</sup>, applied to the absolute change from drifted pre-trade weights</td></tr>
  </tbody>
</table>
