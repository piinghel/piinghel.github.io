---
layout: post
title: "When Risk Limits Start Changing the Portfolio"
description: "Do weight limits leave concentrated portfolio risk? Testing what stock, sector and PCA risk caps reduce, and how much they change the portfolio."
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

<p class="article-summary">My portfolio already limits stock and sector weights. Here I check whether it still takes too much risk in one direction, and what happens when I limit risk contributions directly. Moderate caps reduce the concentrations I find without changing much else; tighter caps reshape the portfolio, with less obvious benefits.</p>

In the [previous article](/quants/2026/08/29/portfolio-optimization.html),
I built an optimizer with limits on volatility, gross exposure, beta, sector
weights, and position size. But limiting how much capital I put into a position
doesn't necessarily limit how much risk it contributes.

The AI rally made me want to check this more closely. Several technology and
semiconductor positions can each meet a weight limit while depending on the
same underlying move. Before adding more constraints, though, I wanted to know:
does my portfolio actually have this problem? And if it does, can I reduce the
concentration without constantly changing the holdings?

Just as in my other articles, I keep the Ridge predictions, selected stocks,
trading controls, execution, and 5 bp charge on traded notional fixed. The
comparison is about allocation. I use three staggered rebalance schedules from
September 1998 through May 2026, reporting results before and after 2021
separately. I had already looked at the later period in earlier work, and added
some tighter thresholds after seeing the first results, so this is an
exploration rather than an untouched test. The three schedules let me check
sensitivity to rebalance timing; they share the same market history.

## Measuring risk contributions

I use three views of risk: individual stocks, sectors, and principal components.
The first two tell me where risk sits among names and industries. Principal
components capture how stocks move together, including shared moves that cross
sector boundaries. For each view, I measure contributions to total forecast
variance.

Let $$w$$ contain the signed portfolio weights, $$\Sigma$$ the current forecast
covariance matrix, and

$$
V(w)=w^\top\Sigma w
$$

the portfolio's forecast variance. The limits use shares of this variance,
even when the portfolio uses less than its maximum risk budget.

For principal component $$k$$, with eigenvalue $$\lambda_k$$ and eigenvector
$$q_k$$, the share is

$$
c_k^{\mathrm{PC}}
=\frac{\lambda_k(q_k^\top w)^2}{V(w)}.
$$

These shares are non-negative and add to one across all components. I estimate
PCA on the stocks eligible at each date, then use the held-stock block of that
covariance in the optimizer. Restricting the factor loadings to those holdings
and keeping every component preserves the full decomposition of portfolio
variance. To separate the effect of a PCA cap from this covariance change, I
compare it with an uncapped optimizer using the same covariance. Stock and
sector caps are compared with the original optimizer.

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
of the book. I put an upper limit on positive contributions and track the total
negative contribution separately. Signed stock contributions sum to one, as do
sector contributions when sectors form a complete partition. A sector's standalone variance,
$$w_S^\top\Sigma w_S$$, answers a different question because it excludes the
sector's covariance with everything else and does not add to total portfolio
variance.

These caps are non-convex because changing the weights changes both the risk
contributions and total variance. I enforce them through successive local
approximations, then recompute the exact shares to check each target. This
checks feasibility, not global optimality. If no target passes, the run stops
rather than using an uncapped fallback.

## Is risk concentrated in this portfolio?

Even with a 4% position limit, a stock can contribute much more than 4% of
portfolio risk. Across the three schedules, the mean 95th percentile of the
largest stock risk contribution is 9.6% in 1998–2021 and 7.2% after 2021.
The corresponding sector figures are 30.8% and
27.3%; for the largest PCA direction, they are 15.6% and 15.4%.

So the weight limits do leave some larger risk contributions. But the portfolio
usually spreads its modeled risk across many directions.
The median effective number of PCA directions,
$$1/\sum_k(c_k^{\mathrm{PC}})^2$$, is about 40. This describes how evenly forecast
risk is spread across components; several components may share an economic
theme. I see a broadly diversified portfolio under this model, with a few
concentrations worth checking more closely.

## How much do risk limits change the portfolio?

At 20%, an all-PC cap would leave almost every rebalance alone: the uncapped
eligible-universe control exceeds it on only 0.69% of rebalances over the full
sample. At 10%, the frequency rises to 13.55%;
at 7.5%, it is 30.20%. These frequencies count breaches in the uncapped
portfolio over the full sample. Table 1 counts corrections in the capped
portfolio after 2021, so the percentages answer different questions.

I also wouldn't stop at the first ten components. They explain the most
variance in the stock universe, but needn't contribute the most risk to this
particular portfolio. Its largest contribution comes from a component after
PC10 on 26.05% of observations, and can come from as far down as PC141.

Sector limits intervene sooner. A 20% cap changes roughly 59% of targets, while
15% changes roughly 98%. A 2% stock cap changes almost every target.
Figure 1 compares how often each tested limit requires an adjustment.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/threshold-impact" mobile="/assets/risk-concentration/threshold-impact_mobile" alt="Paired dots comparing the percentage of rebalances requiring adjustment under each PCA, sector and stock risk cap, in the development and later periods" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 1: How often do risk caps require an adjustment?</strong> Means across three schedules. Development: September 1998–December 2021; later: January 2022–May 2026. * Solver warnings for Sector 15%, Stock 4% and Stock 6%; execution not audited for PCA 7.5% and Stock 3%.</p>

PCA caps intervene more often in the later period. But a cap that requires
frequent small adjustments is different from one that reshapes the holdings.
Table 1 helps separate the two.

The caps apply to target weights using the covariance estimated at that
rebalance. Rounding, execution, and subsequent price moves can take the actual
portfolio above a cap before it trades again.

“Own concentration” is the 95th percentile of the largest contribution in the
dimension being capped, averaged across schedules. “Targets corrected” counts
rebalances that needed a local correction. Target L1 adds the absolute weight
differences between capped and control targets on the same date. These
portfolios evolve independently, so it includes differences built up over time,
not just the adjustment at that rebalance. Executed turnover is in Table 2.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 1: What the tested limits change.</strong> January 2022–May 2026, matched rebalance targets. Concentration is a share of forecast variance; target L1 is a percentage of capital. Corrections use a 10<sup>−6</sup> tolerance. * Solver warnings for Sector 15% and Stock 4%; Stock 3% execution not audited.</caption>
  <thead>
    <tr><th>Configuration</th><th>Matched control</th><th>Own concentration<br>control → capped</th><th>Targets corrected</th><th>Mean target L1</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">All PCs · 10%</th><td>PCA covariance control</td><td>15.88% → 10.00%</td><td>27.1%</td><td>4.8%</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>Original optimizer</td><td>27.28% → 20.00%</td><td>58.1%</td><td>6.6%</td></tr>
    <tr><th scope="row">Sector · 15%*</th><td>Original optimizer</td><td>27.28% → 15.00%</td><td>98.3%</td><td>19.4%</td></tr>
    <tr><th scope="row">Stock · 4%*</th><td>Original optimizer</td><td>7.17% → 4.00%</td><td>50.7%</td><td>4.1%</td></tr>
    <tr><th scope="row">Stock · 3%*</th><td>Original optimizer</td><td>7.17% → 3.00%</td><td>83.4%</td><td>7.1%</td></tr>
    <tr><th scope="row">Stock · 2%</th><td>Original optimizer</td><td>7.17% → 2.00%</td><td>100.0%</td><td>17.0%</td></tr>
  </tbody>
</table>

The 20% sector cap corrects targets fairly often, yet its average target
difference is 6.6% of capital, versus 19.4% at a 15% cap. That distinction
matters to me: I want to limit an exposure without making the cap determine
the allocation at almost every rebalance.

A stock cap also leaves open the question of shared risk. Figure 2 compares
all three dimensions under the 2% stock cap. The later 95th
percentile of the largest stock contribution falls from 7.17% to 2%, while the
corresponding PCA statistic rises from 15.44% to 16.05%. Smaller stock
contributions can still add up to a large shared exposure.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/risk-migration" mobile="/assets/risk-concentration/risk-migration_mobile" alt="Before-and-after dot plot comparing the 95th percentile of the largest PCA, sector, and stock forecast-variance contributions under the original optimizer and a 2% stock risk cap" version="1" %}
</div>

<p class="figure-caption"><strong>Figure 2: Lower stock concentration can coexist with shared risk.</strong> January 2022–May 2026. Schedule-mean 95th percentiles of the largest contributions to forecast variance, measured at rebalance targets. These compare distributions across dates, not a same-date transfer of risk.</p>

## What does it cost?

Moderate caps leave net return, volatility, Sharpe, and turnover close to their
controls (Table 2). PCA uses its matching covariance control; stock and sector
caps use the original optimizer.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Returns, risk, and trading.</strong> Three-schedule means, except Sector 10%**. Net returns are geometric, after 5 bp trading costs. Return, volatility, and two-way turnover are annualized; turnover is a multiple of capital.</caption>
  <thead>
    <tr><th>Portfolio</th><th>Net return</th><th>Vol.</th><th>Net Sharpe</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Original</th><td>12.32%</td><td>8.40%</td><td>1.43</td><td>28.2×</td></tr>
    <tr><th scope="row">PCA control</th><td>12.22%</td><td>8.33%</td><td>1.43</td><td>28.0×</td></tr>
    <tr><th scope="row">PCA 10%</th><td>12.21%</td><td>8.32%</td><td>1.43</td><td>28.0×</td></tr>
    <tr><th scope="row">Sector 20%</th><td>12.40%</td><td>8.40%</td><td>1.43</td><td>28.2×</td></tr>
    <tr><th scope="row">Sector 15%*</th><td>12.30%</td><td>8.40%</td><td>1.42</td><td>28.3×</td></tr>
    <tr><th scope="row">Sector 10%**</th><td>11.06%</td><td>8.27%</td><td>1.31</td><td>28.6×</td></tr>
    <tr><th scope="row">Stock 4%*</th><td>12.34%</td><td>8.42%</td><td>1.42</td><td>28.3×</td></tr>
    <tr><th scope="row">Stock 3%</th><td>12.30%</td><td>8.44%</td><td>1.42</td><td>28.4×</td></tr>
    <tr><th scope="row">Stock 2%</th><td>12.26%</td><td>8.47%</td><td>1.41</td><td>28.7×</td></tr>
    <tr class="period-heading"><th colspan="5">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Original</th><td>7.99%</td><td>9.32%</td><td>0.87</td><td>24.6×</td></tr>
    <tr><th scope="row">PCA control</th><td>8.11%</td><td>9.32%</td><td>0.88</td><td>24.5×</td></tr>
    <tr><th scope="row">PCA 10%</th><td>8.12%</td><td>9.30%</td><td>0.88</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector 20%</th><td>8.18%</td><td>9.29%</td><td>0.89</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector 15%*</th><td>8.17%</td><td>9.24%</td><td>0.89</td><td>24.7×</td></tr>
    <tr><th scope="row">Sector 10%**</th><td>8.12%</td><td>9.10%</td><td>0.90</td><td>25.3×</td></tr>
    <tr><th scope="row">Stock 4%*</th><td>8.11%</td><td>9.31%</td><td>0.88</td><td>24.6×</td></tr>
    <tr><th scope="row">Stock 3%</th><td>8.30%</td><td>9.32%</td><td>0.90</td><td>24.7×</td></tr>
    <tr><th scope="row">Stock 2%</th><td>8.60%</td><td>9.30%</td><td>0.93</td><td>24.9×</td></tr>
  </tbody>
</table>

<p class="figure-caption">* Sector 15% and Stock 4% have solver warnings.<br>** Sector 10%: one completed schedule, with solver and convergence warnings. Testing stopped.</p>

With moderate caps, performance and trading stay close to the matching control.
That leaves little historical performance gain, but also little observed cost
for reducing the modeled concentration. The caps don't fix the gap between
forecast and realized volatility: despite the 7% forecast target, realized
volatility remains near 8.4% before 2022 and 9.3% afterward.

I pushed the sector cap down to 10% to see what a stricter limit would do. In
the only completed schedule, it requires a correction at every rebalance.
The later 95th percentile of the largest sector contribution falls from 28.6%
to 10%, but the corresponding
PCA contribution barely changes, from 14.6% to 14.2%.

Against the original optimizer on that same schedule, net Sharpe falls from
1.40 to 1.31 in development and from 0.93 to 0.90 later.
Later maximum drawdown improves from 9.16% to 7.47%,
while earlier drawdown worsens slightly and turnover rises in both periods.
The next schedule could not find a solution within the iteration limit.
The runs were taking too long, and the result was not
promising enough to justify continuing, so I abandoned the 10% sector test.

The 2% stock cap looks more appealing if I focus on the later period. Net Sharpe
rises from 0.87 to 0.93 and maximum drawdown falls from 9.05% to 8.47%, but the improvement
is uneven across schedules. Development-period Sharpe declines, annual turnover
rises by about 0.55 times capital per year, and cumulative net return is about
0.69 percentage points lower in the technology unwind and 1.06 points lower in
the financial-crisis/rebound window. I wouldn't choose it just for that higher
later Sharpe.

## What happens to the other risks?

I don't want to remove the low-volatility tilt that the strategy is meant to
take. That tilt can span several principal components, while each component
can mix low volatility with sector and market exposure. PCA tells me how
modeled risk is distributed, but doesn't name the economic bet behind it.

As a simple check, I look at whether the shorts are still more volatile than the longs.
For each book, I take the geometric mean of stock forecast volatility, weighted
by each position's share of that book's absolute weights.
The short-to-long ratio is 1.58 before 2022 and
1.75 later under the original optimizer; under the 2% stock cap it is still
1.56 and 1.73. The intended low-volatility tilt remains clear. This ratio
compares the stocks' volatilities; measuring how much portfolio risk comes from
that tilt would require factor attribution.

## Would I add these limits?

For now, I'd monitor these concentrations rather than add all the caps. PCA
10% looks like a reasonable backstop: it cuts the concentration tail under the
model with little change in performance or trading. I don't need it to improve
historical Sharpe to find it useful. But before adopting it, I want to know
whether it limits the risks that concern me. Lower concentration under the
model leaves that question open.

That's why I want to work on portfolio attribution next. The AI rally prompted
this investigation, but these tests don't tell me whether technology, momentum,
or another theme is driving the portfolio. Tracing forecast risk and realized
profit and loss to stocks, sectors, and styles would get me closer to that
question.
