---
layout: post
title: "When Risk Limits Start Changing the Portfolio"
description: "Risk-contribution limits can protect a long-short optimizer, but tight limits move risk elsewhere and increase trading."
date: 2026-09-05
categories: ["Portfolio construction"]
article_label: Portfolio construction · Risk concentration
permalink: /quants/2026/09/05/risk-concentration.html
series_previous: /quants/2026/08/29/portfolio-optimization.html
series_next: /quants/2025/05/10/rebalancing-luck.html
published: true
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">A weight limit tells me how much capital is in a position, not how much risk it contributes. I test whether risk limits can stop one stock, sector, or shared market move from dominating the portfolio without getting in the way on most rebalances. The evidence so far suggests that the existing optimizer already spreads modeled risk reasonably well: moderate caps change little, while strict caps become new sizing rules. This is an exploratory study on reused history.</p>

The [existing optimizer](/quants/2026/08/29/portfolio-optimization.html)
controls total forecast volatility, gross exposure, beta, sector capital, and
position size. It does not answer who supplies the risk. A portfolio can stay
inside its 7% forecast-volatility budget while one stock, sector, or shared
direction supplies a large fraction of that risk. The technology rally around
AI made the distinction practical: several acceptable technology or
semiconductor weights can still depend on the same underlying move. I wanted to
know whether the existing limits left similar concentration in this strategy.
The practical question is: can I stop one stock, sector, or shared
market move from dominating the portfolio's risk without constantly changing
the portfolio?

I keep the Ridge predictions, selected stocks, trading controls, execution, and
5 bp charge on traded notional fixed. Because PCA directions come from the
eligible universe, I measure PCA effects against a matched no-cap covariance
control; stock and sector effects use the original optimizer. The comparison
runs the complete strategy on three
staggered rebalance schedules from September 1998 through May 2026. I report
September 1998–December 2021 and January 2022–May 2026 separately. Both periods
are exploratory: the later history has already informed this research programme,
and I added some tighter thresholds after inspecting the first results.

## Measuring where risk sits

Let $$w$$ contain the signed portfolio weights, $$\Sigma$$ the current forecast
covariance matrix, and

$$
V(w)=w^\top\Sigma w
$$

the portfolio's forecast variance. Every limit below uses a share of this actual
variance. It therefore keeps the same meaning when the portfolio uses less than
its maximum risk budget.

For principal component $$k$$, with eigenvalue $$\lambda_k$$ and eigenvector
$$q_k$$, the share is

$$
c_k^{\mathrm{PC}}
=\frac{\lambda_k(q_k^\top w)^2}{V(w)}.
$$

These shares are non-negative and add to one across all components. The PCA is
estimated on the contemporaneously eligible index universe. I use the
held-stock block of that same covariance in the optimizer and restrict all
full-universe factor loadings to the held names. Keeping all full-universe
factors reconstructs the optimizer covariance, so their contributions still add
to one. This is why the PCA tests need a matched no-cap covariance control.

The stock contribution is its signed Euler allocation of variance,

$$
c_i^{\mathrm{stock}}
=\frac{w_i(\Sigma w)_i}{V(w)},
$$

and a sector contribution adds those allocations within sector $$S$$,

$$
c_S^{\mathrm{sector}}
=\frac{w_S^\top\Sigma w}{V(w)}
=\sum_{i\in S}c_i^{\mathrm{stock}}.
$$

Stock and sector contributions can be negative when a position hedges the rest
of the book. I cap positive contributions from above and retain the negative
mass as a diagnostic. Signed stock contributions sum to one, as do sector
contributions when sectors form a complete partition. A sector's standalone variance,
$$w_S^\top\Sigma w_S$$, answers a different question because it excludes the
sector's covariance with everything else and does not add to total portfolio
variance.

These ratios make the hard caps non-convex because the denominator changes with
the weights. I first solve the original optimizer, then use a bounded sequence
of conservative local convex approximations. After every candidate, I recompute
the exact shares from $$w^\top\Sigma w$$. Any candidate whose exact cap excess
remains above $$10^{-6}$$ is rejected; feasible targets with solver or
outer-convergence warnings remain provisional. This verifies the returned
target within tolerance without claiming a globally optimal solution. If no
candidate passes the exact check, the run marks the arm incomplete rather than
using the uncapped target or scaling it: scaling changes variance, but not a
variance share.

## When the limits begin to bind

The uncapped optimizer confirms that weight and risk limits are not equivalent.
Across the three schedules, the mean 95th percentile of the largest stock risk
contribution is 9.6% in 1998–2021 and 7.2% after 2021, even though each stock's
absolute weight is capped at 4%. The corresponding sector figures are 30.8% and
27.3%; for the largest PCA direction, they are 15.6% and 15.4%. This is enough
concentration to justify testing a guardrail, without implying that every date
or every dimension has a serious problem. The median effective number of PCA
directions, $$1/\sum_k(c_k^{\mathrm{PC}})^2$$, is about 40. This describes
dispersion within the forecast covariance model, not economic diversification.

Over the full sample, the uncapped eligible-universe control exceeds a 20%
all-PC limit on only 0.69% of rebalances. At 10%, the frequency rises to 13.55%;
at 7.5%, it is 30.20%. These unconditional control breaches differ from Table
1's later-period correction frequency, which follows the constrained
portfolio's own path. Looking only at the first ten components would miss part
of this tail.
The component making the largest portfolio risk contribution lies after PC10 on
26.05% of observations; ranked by covariance eigenvalue, it can be as late as
PC141.

Sector limits intervene sooner. A 20% cap changes roughly 59% of targets, while
15% changes roughly 98% and is close to continuously active. A 2% stock cap
changes almost every target. The amount moved matters as well as the frequency:
an optimizer can make a small correction on many dates without rebuilding the
portfolio. The capped and control targets have an average L1 distance of 1.5%
of capital for PCA 10% in the development period and 4.8% later. The distance
is roughly 7% for Sector 20% in both periods, nearly 20% for Sector 15%, and
26.5% before 2022 and 17.0% later for Stock 2%. Because the two strategies
evolve independently, these are path differences rather than the immediate
size of a single rebalance correction.

These are rebalance-target controls. Rounding, execution, and subsequent price
moves can take the carried portfolio above a cap before the next rebalance. I
treat those as implementation and drift outcomes. The optimizer's narrower
question is whether the chosen target satisfies the requested share using that
date's covariance matrix.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 1: What the tested limits change.</strong> January 2022–May 2026. “Own concentration” is the mean across schedules of the 95th percentile of the largest contribution in the capped dimension, measured on matched targets before and after the cap. “Targets corrected” means the path-dependent constrained run required a local correction. Target L1 compares the independently run control and capped targets on the same dates; it is the sum of absolute weight changes as a percentage of capital, not executed turnover. Corrections and residual violations use a 10<sup>−6</sup> tolerance. Sector 15%* remains provisional because one target returned an inaccurate-optimum status, although its reconstructed constraints held.</caption>
  <thead>
    <tr><th>Configuration</th><th>Matched control</th><th>Own concentration<br>control → capped</th><th>Targets corrected</th><th>Mean target L1</th><th>Residual violations</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">All PCs · 10%</th><td>PCA covariance control</td><td>15.88% → 10.00%</td><td>27.1%</td><td>4.8%</td><td>0</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>Original optimizer</td><td>27.28% → 20.00%</td><td>58.1%</td><td>6.6%</td><td>0</td></tr>
    <tr><th scope="row">Sector · 15%*</th><td>Original optimizer</td><td>27.28% → 15.00%</td><td>98.3%</td><td>19.4%</td><td>0</td></tr>
    <tr><th scope="row">Stock · 2%</th><td>Original optimizer</td><td>7.17% → 2.00%</td><td>100.0%</td><td>17.0%</td><td>0</td></tr>
  </tbody>
</table>

The strict stock test also shows why one concentration measure is not enough.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/risk-migration" mobile="/assets/risk-concentration/risk-migration_mobile" alt="Before-and-after dot plot comparing the 95th percentile of the largest PCA, sector, and stock forecast-variance contributions under the original optimizer and a 2% stock risk cap" version="1" %}
</div>

<p class="figure-caption"><strong>Figure 1: A stock cap narrows one dimension, not all of them.</strong> January 2022–May 2026. Values are means across three schedule-level 95th percentiles at rebalance targets, on a common forecast-variance scale. They show a cross-dimensional trade-off, not a same-date flow of risk.</p>

## Protection, performance, and trading

Table 2 keeps performance beside the risk-control result. Returns are annualized
geometric returns, matching the preceding article; net returns deduct the
trading charge. Every number is first calculated for a full-capital schedule,
then averaged across the three schedules. Maximum drawdown is likewise the mean
of three schedule-level maximum drawdowns.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: Performance and trading under concentration limits.</strong> Means of three schedule-level metrics. Returns are geometric and annualized; realized volatility is annualized. Net results charge 5 bp on traded notional. Turnover is two-way executed turnover, annualized. Drawdowns are positive loss magnitudes. The PCA covariance control has no concentration cap. Sector 15%* retains the provisional status defined in Table 1; Stock 2% is the audited strict counterexample.</caption>
  <thead>
    <tr><th>Constraint</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Realized vol.</th><th>Max net DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="7">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Optimizer + trading controls</th><td>13.92%</td><td>12.32%</td><td>1.43</td><td>8.40%</td><td>18.06%</td><td>28.2×</td></tr>
    <tr><th scope="row">PCA covariance control · no cap</th><td>13.80%</td><td>12.22%</td><td>1.43</td><td>8.33%</td><td>18.24%</td><td>28.0×</td></tr>
    <tr><th scope="row">All PCs · 10%</th><td>13.79%</td><td>12.21%</td><td>1.43</td><td>8.32%</td><td>18.22%</td><td>28.0×</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>13.99%</td><td>12.40%</td><td>1.43</td><td>8.40%</td><td>18.02%</td><td>28.2×</td></tr>
    <tr><th scope="row">Sector · 15%*</th><td>13.90%</td><td>12.30%</td><td>1.42</td><td>8.40%</td><td>18.29%</td><td>28.3×</td></tr>
    <tr><th scope="row">Stock · 2%</th><td>13.89%</td><td>12.26%</td><td>1.41</td><td>8.47%</td><td>18.01%</td><td>28.7×</td></tr>
    <tr class="period-heading"><th colspan="7">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Optimizer + trading controls</th><td>9.33%</td><td>7.99%</td><td>0.87</td><td>9.32%</td><td>9.05%</td><td>24.6×</td></tr>
    <tr><th scope="row">PCA covariance control · no cap</th><td>9.45%</td><td>8.11%</td><td>0.88</td><td>9.32%</td><td>9.14%</td><td>24.5×</td></tr>
    <tr><th scope="row">All PCs · 10%</th><td>9.47%</td><td>8.12%</td><td>0.88</td><td>9.30%</td><td>9.11%</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>9.52%</td><td>8.18%</td><td>0.89</td><td>9.29%</td><td>9.03%</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector · 15%*</th><td>9.52%</td><td>8.17%</td><td>0.89</td><td>9.24%</td><td>8.98%</td><td>24.7×</td></tr>
    <tr><th scope="row">Stock · 2%</th><td>9.96%</td><td>8.60%</td><td>0.93</td><td>9.30%</td><td>8.47%</td><td>24.9×</td></tr>
  </tbody>
</table>

The displayed moderate limits leave realized volatility, drawdown, and turnover
close to the corresponding control. They mainly redistribute forecast risk
inside a portfolio that already uses almost all of its 7% forecast budget. I do
not see evidence here that another hard limit improves historical performance
as a whole, but that is not the guardrail's test. The limits also do not repair
the risk model's level: realized volatility remains near 8.4% before 2022 and
9.3% afterward.

The 2% stock cap is more consequential. Its later net Sharpe rises from 0.87 to
0.93 and later maximum drawdown falls from 9.05% to 8.47%, but the improvement
is uneven across schedules. Development-period Sharpe declines, annual turnover
rises by about 0.55 times capital per year, and cumulative net return is about
0.69 percentage points lower in the technology unwind and 1.06 points lower in
the financial-crisis/rebound window. I do not treat the best later Sharpe as a
selection rule.

## Risk moves rather than disappearing

The 2% stock cap lowers the later 95th percentile of the largest stock
contribution from 7.17% to 2%. The corresponding PCA statistic rises by about
0.6 percentage points, from 15.44% to 16.05%. Many small stock allocations can
still load on the same correlated direction. The cap succeeds on its own
definition without producing a corresponding reduction in PCA concentration.

PCA directions and economically named styles can overlap without being
interchangeable. A low-volatility tilt can span several current principal
components, while a principal component can mix low volatility with sector and
market structure. PCA supplies an additive decomposition of the current risk
model. A style exposure supplies an economic interpretation.

As a descriptive low-volatility diagnostic, I compare the shorts' and longs'
geometric mean stock forecast volatility, weighting each leg by positive
within-book weight magnitudes. The short-to-long ratio is 1.58 before 2022 and
1.75 later under the original optimizer; under the 2% stock cap it is still
1.56 and 1.73. This is not a factor loading or risk attribution. It simply shows
that the intended low-volatility ordering remains substantial.

## Guardrail or diagnostic?

The study establishes that the caps work on their stated forecast-risk measure.
PCA 10%, for example, lowers the later concentration tail from 15.88% to 10%,
with similar realized performance and trading and an average 4.8% target L1
distance from its control. Sector 20% achieves its own limit with a larger but
still moderate target difference. Sector 15% and Stock 2% are different: they
act on nearly every target and behave more like sizing rules.

What the history does not establish is whether these modeled reductions protect
against a future economic loss or a risk-model error. A guardrail need not raise
historical Sharpe to be useful, but its protection should match a risk I care
about. My current preference is therefore monitoring first, with PCA 10% or a
similarly moderate limit available as a selective backstop rather than an
automatic portfolio rule.

Concentration is also only one part of the question raised by the AI rally. PCA
can reveal a shared direction without naming its economic source. The next step
is portfolio attribution: trace forecast risk and realized profit and loss to
stocks, sectors, and styles, then test whether technology, momentum, or another
theme is actually driving the book.

These thresholds were inspected on one reused market history. The three
rebalance schedules expose timing sensitivity, but they are not independent
market samples. New data and attribution, rather than the highest historical
Sharpe in this grid, should decide whether any candidate belongs in the
allocator.
