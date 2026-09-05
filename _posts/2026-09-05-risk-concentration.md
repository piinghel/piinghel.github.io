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

<p class="article-summary">Weight limits can leave a portfolio exposed to concentrated risk. I check whether this happens in the existing strategy, then test what stock, sector and PCA risk caps change. The optimizer spreads forecast risk reasonably well, but some concentrations remain. Moderate caps reduce them with limited changes to the holdings; tighter caps have a larger effect on position sizing.</p>

The [existing optimizer](/quants/2026/08/29/portfolio-optimization.html)
controls total forecast volatility, gross exposure, beta, sector capital, and
position size. A portfolio can meet all those limits while one stock, sector,
or shared market move accounts for a large fraction of its risk. The AI rally
prompted me to look at this: technology and semiconductor positions can each
meet a weight limit while depending on the same underlying move.

Does this happen in our portfolio despite its existing weight limits? If so,
can risk limits reduce the concentration without constantly changing the
holdings?

Just as in my other articles, I keep the Ridge predictions, selected stocks,
trading controls, execution, and 5 bp charge on traded notional fixed.
I run the full strategy
on three staggered rebalance schedules from September 1998 through May 2026.
I report September 1998–December 2021 and January 2022–May 2026 separately.
This is exploratory: I had already examined the later period in earlier work
and added some tighter thresholds after seeing the first results.

## Measuring risk contributions

I look at concentration in three ways. Stock contributions tell me whether a
single name dominates; sector contributions group those names by industry.
Principal components give me another view, based on how stocks move together.
They can pick up shared risk that crosses the sector boundaries. In each case,
I need the contribution as a share of the portfolio's total forecast variance.

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
checks feasibility, not global optimality. If no target passes, the
configuration remains incomplete rather than using an uncapped fallback.
Solver or convergence warnings keep a result provisional.

## Is risk concentrated in this portfolio?

Even with a 4% position limit, a stock can contribute much more than 4% of
portfolio risk. Across the three schedules, the mean 95th percentile of the
largest stock risk contribution is 9.6% in 1998–2021 and 7.2% after 2021.
The corresponding sector figures are 30.8% and
27.3%; for the largest PCA direction, they are 15.6% and 15.4%.

Still, the portfolio usually spreads its modeled risk across many directions.
The median effective number of PCA directions,
$$1/\sum_k(c_k^{\mathrm{PC}})^2$$, is about 40. This describes how evenly forecast
risk is spread across components; several components may share an economic
theme. The portfolio is broadly diversified under this model, with some larger
contributions worth examining.

## How much do risk limits change the portfolio?

At 20%, an all-PC cap would leave almost every rebalance alone: the uncapped
eligible-universe control exceeds it on only 0.69% of rebalances over the full
sample. At 10%, the frequency rises to 13.55%;
at 7.5%, it is 30.20%. These frequencies ask how often the uncapped portfolio
would break each limit. Table 1 instead counts corrections along the capped
portfolio's own path in the later period. Looking only at the first ten
components would miss part of this tail. The component making the largest
portfolio risk contribution lies after PC10 on
26.05% of observations; ranked by covariance eigenvalue, it can be as late as
PC141.

Sector limits intervene sooner. A 20% cap changes roughly 59% of targets, while
15% changes roughly 98%. A 2% stock cap changes almost every target.
Figure 1 compares how often each tested limit requires an adjustment.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/threshold-impact" mobile="/assets/risk-concentration/threshold-impact_mobile" alt="Paired dots comparing the percentage of rebalances requiring adjustment under each PCA, sector and stock risk cap, in the development and later periods" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 1: How often do risk caps require an adjustment?</strong> Means across three schedules. Development: September 1998–December 2021; later: January 2022–May 2026. * Provisional results.</p>

PCA caps intervene more often in the later period. Frequency alone does not
tell me how different the holdings become; Table 1 adds that comparison.

The caps apply to target weights using the covariance estimated at that
rebalance. Rounding, execution, and subsequent price moves can take the actual
portfolio above a cap before it trades again.

Table 1 puts the reduction in concentration beside the frequency and size of
the portfolio changes. “Own concentration” follows the largest contribution in
the dimension being capped: I take its 95th percentile within each schedule,
then average the three. “Targets corrected” counts rebalances where the capped
run needed a local correction. Target L1 adds the absolute weight differences
between the capped and control targets on the same date. Each portfolio evolves
independently, so the distance includes differences accumulated since earlier
rebalances. Executed turnover appears separately in Table 2.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 1: What the tested limits change.</strong> January 2022–May 2026, matched rebalance targets. Concentration is a share of forecast variance; target L1 is a percentage of capital. Corrections and residual violations use a 10<sup>−6</sup> tolerance. Sector 15%* remains provisional: one target returned an inaccurate-optimum status, although its reconstructed constraints held.</caption>
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

Figure 2 compares all three dimensions under the 2% stock cap. The later 95th
percentile of the largest stock contribution falls from 7.17% to 2%, while the
corresponding PCA statistic rises from 15.44% to 16.05%. Smaller stock
contributions can still add up to a large shared exposure.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/risk-migration" mobile="/assets/risk-concentration/risk-migration_mobile" alt="Before-and-after dot plot comparing the 95th percentile of the largest PCA, sector, and stock forecast-variance contributions under the original optimizer and a 2% stock risk cap" version="1" %}
</div>

<p class="figure-caption"><strong>Figure 2: Lower stock concentration can coexist with shared risk.</strong> January 2022–May 2026. Each value is the mean across three schedules of the 95th percentile of the largest contribution, measured at rebalance targets. All contributions are shares of forecast variance. These summaries compare distributions across dates; they do not trace a transfer of risk on individual dates.</p>

## Protection, performance, and trading

How much do these changes cost in return and trading? Table 2 compares each
capped portfolio with its control. I calculate each metric, including maximum
drawdown, for each full-capital schedule before averaging the three.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: Performance and trading under concentration limits.</strong> Means of three schedule-level metrics. Returns are geometric and annualized; realized volatility is annualized. Net results charge 5 bp on traded notional. Turnover is two-way executed turnover, annualized. Drawdowns are positive loss magnitudes. The PCA covariance control has no concentration cap. Sector 15%* remains provisional as explained in Table 1.</caption>
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

The moderate limits leave realized volatility, drawdown, and turnover
close to the corresponding control. They mainly redistribute forecast risk
inside a portfolio that already uses almost all of its 7% forecast budget. I
see little overall performance benefit from adding a cap. Nor does it close
the gap between forecast and realized risk: volatility remains near 8.4%
before 2022 and 9.3% afterward.

The 10% sector cap is a deliberately strict test. In the first completed
schedule, it requires a correction at every rebalance. The later 95th percentile
of the largest sector contribution falls from 28.6% to 10%, but the corresponding
PCA contribution barely changes, from 14.6% to 14.2%.

Against the original optimizer on that same schedule, net Sharpe falls from
1.40 to 1.31 in development
and from 0.93 to 0.90 later. Later maximum drawdown improves from 9.16% to 7.47%,
while earlier drawdown worsens slightly and turnover rises in both periods.
I consider this too strict for the occasional guardrail I want, so I am not
adding it to the portfolio.

These 10% results are preliminary and separate from the three-schedule figures
and tables above. The saved sector shares pass the cap check, but solver and
convergence warnings remain, and execution still requires audit.

The 2% stock cap has a different trade-off. Its later net Sharpe rises from 0.87 to
0.93 and later maximum drawdown falls from 9.05% to 8.47%, but the improvement
is uneven across schedules. Development-period Sharpe declines, annual turnover
rises by about 0.55 times capital per year, and cumulative net return is about
0.69 percentage points lower in the technology unwind and 1.06 points lower in
the financial-crisis/rebound window. Those trade-offs give me little reason
to choose it on the strength of its later Sharpe alone.

## What happens to the other risks?

What connects the stocks behind that shared exposure? The strategy's
low-volatility tilt can span several principal
components, while a principal component can mix low volatility with sector and
market structure. PCA divides up modeled risk, but it cannot by itself tell me
which economic theme the portfolio depends on.

As a simple check, I look at whether the shorts are still more volatile than the longs.
For each book, I take the geometric mean of stock forecast volatility, weighted
by each position's share of that book's absolute weights.
The short-to-long ratio is 1.58 before 2022 and
1.75 later under the original optimizer; under the 2% stock cap it is still
1.56 and 1.73. The intended low-volatility tilt remains clear. This ratio
compares the stocks' volatilities; measuring how much portfolio risk comes from
that tilt would require factor attribution.

## Guardrail or diagnostic?

I would start by monitoring these concentrations. PCA 10%, or a similarly
moderate limit, is a plausible backstop when I want extra protection. Before
using it routinely, though, I want to be able to explain what loss I am trying
to prevent. I can accept a cap that adds no historical Sharpe if it protects
against a risk I care about. Lower concentration in the model is a useful
starting point for that decision, but the model may itself miss the risk.

Concentration is also only one part of the question raised by the AI rally. PCA
can reveal a shared direction without naming its economic source. The next step
is portfolio attribution: trace forecast risk and realized profit and loss to
stocks, sectors, and styles, then test whether technology, momentum, or another
theme is actually driving the book.

The three schedules show how much these choices depend on rebalance timing;
they still share one market history. I would want attribution and new data
before making a concentration cap a routine part of the allocator.
