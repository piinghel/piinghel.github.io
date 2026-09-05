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
published: false
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">A portfolio-level volatility limit does not stop one stock, sector, or correlated direction from carrying a large part of forecast risk. I add separate concentration limits to the state-aware optimizer. Completed tests so far show that moderate limits can reduce the intended tail without changing the portfolio much, while a strict stock limit trades more and moves risk into correlated directions. This is an exploratory study on reused history, not a new allocator selection.</p>

The [state-aware optimizer](/quants/2026/08/29/portfolio-optimization.html)
controls total forecast volatility, gross exposure, beta, sector capital, and
position size. Those limits still leave a practical question. A portfolio can
stay inside its 7% forecast-volatility budget while one stock, sector, or shared
direction supplies a large fraction of that risk. How restrictive must another
limit be before it changes the book, and what does the protection cost?

I keep the Ridge predictions, selected stocks, trading controls, execution, and
5 bp charge on traded notional fixed. Stock and sector tests retain the original
selected-universe covariance. PCA tests estimate covariance on the full
point-in-time eligible universe, so I compare them with an otherwise uncapped
eligible-universe control. The comparison runs the complete strategy on three
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
estimated on the contemporaneously eligible index universe, then restricted to
the stocks held by the portfolio. This avoids defining the directions from the
same extreme rank tails whose concentration I want to measure.

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

PCA directions and economically named styles can overlap without being
interchangeable. A low-volatility tilt can span several current principal
components, while a principal component can mix low volatility with sector and
market structure. PCA supplies an additive decomposition of the current risk
model. A style exposure supplies an economic interpretation. I monitor the
strategy's low-volatility tilt rather than forcing it to zero.

## When the limits begin to bind

The uncapped eligible-universe portfolio exceeds a 20% all-PC limit on only
0.69% of rebalances. At 10%, the frequency rises to 13.55%; at 7.5%, it is
30.20%. Looking only at the first ten components would miss part of this tail.
The portfolio's largest component lies after PC10 on 26.05% of observations and
can rank as late as PC141.

Sector limits intervene sooner. A 20% cap changes roughly 59% of targets, while
15% changes roughly 98% and is close to continuously active. A 2% stock cap
changes almost every target. The amount moved matters as well as the frequency:
an optimizer can make a small correction on many dates without rebuilding the
portfolio.

<!-- FINAL EVIDENCE SLOT: insert the audited light/dark threshold-impact figure.
     It shows correction frequency, target L1 change, and net-Sharpe change for
     every tested PCA, sector, and stock threshold, with schedule min/max ranges. -->

<!-- FINAL CAPTION SLOT: Figure 1. Define periods, schedule ranges, covariance
     controls, 5 bp costs, provisional solver markers, and exploratory additions. -->

## Protection, performance, and trading

Table 1 keeps performance beside the risk-control result. Returns are annualized
geometric returns, matching the preceding article; net returns deduct the
trading charge. Every number is first calculated for a full-capital schedule,
then averaged across the three schedules. Maximum drawdown is likewise the mean
of three schedule-level maximum drawdowns.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 1: Performance and trading under moderate limits.</strong> Means of three schedule-level metrics. Returns are geometric and annualized; realized volatility is annualized. Net results charge 5 bp on traded notional. Turnover is two-way executed turnover, annualized. Drawdowns are positive loss magnitudes. The final stock row remains pending completion and audit.</caption>
  <thead>
    <tr><th>Constraint</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Realized vol.</th><th>Max net DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="7">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Optimizer + trading controls</th><td>13.92%</td><td>12.32%</td><td>1.43</td><td>8.40%</td><td>18.06%</td><td>28.2×</td></tr>
    <tr><th scope="row">Eligible-universe covariance control</th><td>13.80%</td><td>12.22%</td><td>1.43</td><td>8.33%</td><td>18.24%</td><td>28.0×</td></tr>
    <tr><th scope="row">All PCs · 10%</th><td>13.79%</td><td>12.21%</td><td>1.43</td><td>8.32%</td><td>18.22%</td><td>28.0×</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>13.99%</td><td>12.40%</td><td>1.43</td><td>8.40%</td><td>18.02%</td><td>28.2×</td></tr>
    <tr class="period-heading"><th colspan="7">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Optimizer + trading controls</th><td>9.33%</td><td>7.99%</td><td>0.87</td><td>9.32%</td><td>9.05%</td><td>24.6×</td></tr>
    <tr><th scope="row">Eligible-universe covariance control</th><td>9.45%</td><td>8.11%</td><td>0.88</td><td>9.32%</td><td>9.14%</td><td>24.5×</td></tr>
    <tr><th scope="row">All PCs · 10%</th><td>9.47%</td><td>8.12%</td><td>0.88</td><td>9.30%</td><td>9.11%</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>9.52%</td><td>8.18%</td><td>0.89</td><td>9.29%</td><td>9.03%</td><td>24.6×</td></tr>
    <!-- FINAL EVIDENCE SLOT: add the audited moderate stock row selected from
         2%, 3%, and 4%, then reassess whether one strict row is needed. -->
  </tbody>
</table>

The completed moderate limits leave realized volatility, drawdown, and turnover
close to the corresponding control. They mainly redistribute forecast risk
inside a portfolio that already uses almost all of its 7% forecast budget. That
is useful protection when the goal is to prevent an unusually dominant bet. It
does not repair the risk model's level: realized volatility remains near 8.4%
before 2022 and 9.3% afterward.

The 2% stock cap is more consequential. Its later net Sharpe rises from 0.87 to
0.93 and later maximum drawdown falls from 9.05% to 8.47%, but the improvement
is uneven across schedules. Development-period Sharpe declines, annual turnover
rises by about 0.55 times capital per year, and cumulative net return is about
0.69 percentage points lower in the technology unwind and 1.06 points lower in
the financial-crisis/rebound window. I do not treat the best later Sharpe as a
selection rule.

## Risk moves rather than disappearing

The 2% stock cap lowers the later 95th percentile of the largest stock
contribution from 7.17% to 2%. At the same time, the 95th percentile of the
largest PCA contribution rises from 15.44% to 16.05%. Many small stock
allocations can still load on the same correlated direction. The cap succeeds
on its own definition while shifting some risk elsewhere.

The intended low-volatility exposure remains substantial under every completed
limit, with only a modest reduction under the 2% stock cap. That distinction
matters here. Removing the strategy's intended tilt would make the portfolio
look more diversified by one measure while changing the return source I meant
to implement.

Target-date compliance also does not guarantee continuous compliance. Rounding,
execution, and subsequent price moves can take the carried portfolio above a
cap before the next rebalance. I treat those as implementation and drift
outcomes. The optimizer's question is narrower: did the chosen target satisfy
the requested share using that date's covariance matrix?

## A moderate guardrail

<!-- FINAL INTERPRETATION SLOT: choose the moderate protective recommendation
     after PCA 7.5%, sector 10%, and stock 3% complete, including solver status,
     stress windows, schedule dispersion, negative contribution mass,
     standalone leg risk, and low-volatility diagnostics. -->

The evidence so far favors limits that cut the historical tail while leaving
the allocator room to express its signal and intended style. PCA 10% and sector
20% behave like guardrails in that sense. A 2% stock cap behaves more like a
continuous portfolio-design rule: it changes almost every target, trades more,
and redirects risk into correlated components.

These thresholds were inspected on one reused market history. The three
rebalance schedules expose timing sensitivity, but they are not independent
market samples. I would use the moderate limits as candidates for forward
monitoring, with the uncapped book and risk-migration diagnostics beside them.
New data, rather than the highest historical Sharpe in this grid, would decide
whether a candidate belongs in the allocator.
