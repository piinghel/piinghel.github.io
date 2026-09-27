---
layout: post
title: "When Risk Limits Start Changing the Portfolio"
description: "Do weight limits leave concentrated portfolio risk? Testing what stock, sector and PCA risk caps reduce, and how much they change the portfolio."
date: 2026-09-05
last_modified_at: 2026-09-27
categories: ["Portfolio construction"]
article_label: Portfolio construction · Risk concentration
permalink: /quants/2026/09/05/risk-concentration.html
published: true
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">The optimizer already limits stock and sector weights. Here I check whether the portfolios it produces still take too much risk in one direction, and what happens when I limit risk contributions directly. Moderate caps reduce the concentrations I find with small changes to holdings and performance; tighter caps reshape the portfolio, with less obvious benefits.</p>

The [optimizer](/quants/2026/08/29/portfolio-optimization.html) already
limits stock and sector weights. But a small position can still carry a lot
of risk, and several small positions can end up making much the same bet.
I wanted to check how much of that the weight limits leave behind.

The AI rally made me want to check this more closely. Several technology and
semiconductor positions can each meet a weight limit while depending on the
same underlying move. Before adding more constraints, though, I wanted to know:
does the backtest show this problem? And if it does, can I reduce the
concentration with limited trading?

As in the [optimizer article](/quants/2026/08/29/portfolio-optimization.html),
I hold fixed an earlier version of the Ridge ranking, the selected stocks,
trading controls, execution and a 5 bp cost on traded notional, so only the
allocation changes. I use three rebalance schedules, each starting
in a different week, from September 1998 through May 2026, reporting results before and after 2021
separately. The three schedules let me check
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

the portfolio's forecast variance. The limits use shares of this variance.

For principal component $$k$$, with eigenvalue $$\lambda_k$$ and eigenvector
$$q_k$$, the share is

$$
c_k^{\mathrm{PC}}
=\frac{\lambda_k(q_k^\top w)^2}{V(w)}.
$$

These shares are non-negative and add to one across all components. The
basis matters. For the original optimizer and the stock and sector caps, I
measure them on the optimizer's own covariance of the selected stocks. A PCA
cap needs components that don't change with the holdings, so there I estimate
PCA on all eligible stocks at each date and give the optimizer the part of
that covariance covering the portfolio's stocks. To separate the cap from that
covariance change, I compare it with an uncapped optimizer using the same
covariance; stock and sector caps are compared with the original optimizer.

A stock's contribution is its weight times its covariance with the portfolio, as a share of total variance (its Euler allocation):

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
negative contribution separately. Stock contributions sum to one, and so do sector contributions when every stock belongs to exactly one sector; the cross-sector covariance terms are what make them add up.

These caps are non-convex, because changing the weights changes both the contributions and total variance. So I enforce them with successive local approximations and then recompute the exact shares. I accept a target only if it meets the caps within tolerance.

## Is risk concentrated in this portfolio?

Even with a 4% position limit, a stock can contribute much more than 4% of
portfolio risk. Across the three schedules, the mean 95th percentile of the
largest stock risk contribution is 9.6% in 1998–2021 and 7.2% after 2021.
The corresponding sector figures are 30.8% and
27.3%; for the largest PCA direction, they are 15.6% and 15.4%.

So the weight limits do leave some larger risk contributions, but the
portfolio usually spreads its modeled risk widely: the median effective number
of PCA directions, $$1/\sum_k(c_k^{\mathrm{PC}})^2$$, is about 40 on the
selected stocks. Several components may still share an economic theme.

Did the AI rally change that? Stock and sector concentration actually fell
after 2021. The shared, cross-sector view is where concentration shows, but it
didn't start with the AI rally. On the eligible-universe components, the
largest one took more than 10% of forecast variance on about 6% of rebalances
before 2015, 31% in 2015–16, 20% in 2017–21 and 28% since 2022, lately mostly
the third and fourth components (Figure 1; tap or hover over a point to see
which). So the book does carry more shared concentration than it used to, in
the direction the weight limits can't see, but it built up well before 2022.

<div id="rc-pc-share" style="width:100%;min-height:280px;margin:1.4rem 0 0.4rem" role="img" aria-label="Largest principal component's share of forecast variance at each rebalance, 1998–2026, with a 10% reference line; shares above 10% become frequent from 2015." data-source="/assets/risk-concentration/pc-share.json?v=1" data-plotly="https://cdn.jsdelivr.net/npm/plotly.js-cartesian-dist-min@3.1.0/plotly-cartesian.min.js"></div>
<noscript><p>This chart needs JavaScript; the paragraph above gives its main numbers.</p></noscript>
<script src="/assets/js/risk-concentration.js?v=2" defer></script>

<p class="figure-caption"><strong>Figure 1: Shared risk has concentrated more often since 2015.</strong> The largest principal component's share of forecast variance at every rebalance of the uncapped optimizer, three schedules pooled, with components from the eligible-universe covariance. Highlighted points exceed 10%; the shaded area is January 2022–May 2026.</p>

## How much do risk limits change the portfolio?

Over the full sample, a cap on every component's share would bind on about 1%
of rebalances at 20%, 13% at 10% and 30% at 7.5%. I cap all components, not
only the leading ones, although the difference is small in practice: when the
largest share exceeds 10%, it comes from the first ten components 94% of the
time and never from beyond the seventeenth.

Sector limits intervene far more often. In 2022–2026, a 20% sector cap corrects
58% of targets and a 15% cap 98%, and a 2% stock cap corrects every one.
Figure 2 compares how often each tested limit requires an adjustment.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/threshold-impact" mobile="/assets/risk-concentration/threshold-impact_mobile" alt="Paired dots comparing the percentage of rebalances requiring adjustment under each PCA, sector and stock risk cap, in the development and later periods" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 2: How often risk caps require an adjustment.</strong> Means across three schedules. Development: September 1998–December 2021; later: January 2022–May 2026. * Solver warnings for Sector 15%, Stock 4% and Stock 6%; checks cover targets only for PCA 7.5% and Stock 3%.</p>

PCA caps intervene more often in the later period. Table 1 puts that frequency
beside the amount of capital each cap reallocates.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 1: What the tested limits change.</strong> January 2022–May 2026, matched rebalance targets. “Own concentration” is the schedule-mean 95th percentile of the largest contribution in the capped dimension, as a share of forecast variance; the PCA cap is measured on eligible-universe components and compared with the uncapped optimizer using the same covariance, the others with the original optimizer. “Corrected” counts targets that needed a correction (10<sup>−6</sup> tolerance). Target L1 adds absolute weight differences from the control on the same date, in percent of capital, including differences that build up as the portfolios drift apart. Caps apply to targets; price moves between rebalances can take holdings above them. Sector 15% and Stock 4% each had a solver warning on one rebalance; Stock 3% checks cover targets only.</caption>
  <thead>
    <tr><th>Cap</th><th>Own concentration</th><th>Corrected</th><th>Target L1</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">All PCs · 10%</th><td>15.9% → 10.0%</td><td>27.1%</td><td>4.8%</td></tr>
    <tr><th scope="row">Sector · 20%</th><td>27.3% → 20.0%</td><td>58.1%</td><td>6.6%</td></tr>
    <tr><th scope="row">Sector · 15%</th><td>27.3% → 15.0%</td><td>98.3%</td><td>19.4%</td></tr>
    <tr><th scope="row">Stock · 4%</th><td>7.2% → 4.0%</td><td>50.7%</td><td>4.1%</td></tr>
    <tr><th scope="row">Stock · 3%</th><td>7.2% → 3.0%</td><td>83.4%</td><td>7.1%</td></tr>
    <tr><th scope="row">Stock · 2%</th><td>7.2% → 2.0%</td><td>100.0%</td><td>17.0%</td></tr>
  </tbody>
</table>

The 20% sector cap corrects most targets, but by little: 6.6% of capital on
average, against 19.4% at 15%. That distinction matters to me: I want a cap
whose corrections are small, leaving most of the sizing to the score and the
covariance model.

A stock cap also doesn't address shared risk. Figure 3 compares
all three dimensions under the 2% stock cap. The 95th percentile of the largest
stock contribution falls from about 7% to 2%, while the largest PCA share
barely moves, at about 15–16%. Smaller stock contributions can still add up to
a large shared exposure.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/risk-concentration/risk-migration" mobile="/assets/risk-concentration/risk-migration_mobile" alt="Before-and-after dot plot comparing the 95th percentile of the largest PCA, sector, and stock forecast-variance contributions under the original optimizer and a 2% stock risk cap" version="2" %}
</div>

<p class="figure-caption"><strong>Figure 3: Lower stock concentration can coexist with shared risk.</strong> January 2022–May 2026. Schedule-mean 95th percentiles of the largest contributions to forecast variance at rebalance targets, with components from the optimizer's covariance of the selected stocks.</p>

## What does it cost?

Moderate caps leave net return, volatility, Sharpe and turnover close to their
controls (Table 2).

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Returns, risk and trading.</strong> Three-schedule means. Net returns are geometric, after 5 bp trading costs. Return, volatility and two-way turnover are annualized; turnover is a multiple of capital. Sector 15% and Stock 4% each had a solver warning on one rebalance.</caption>
  <thead>
    <tr><th>Portfolio</th><th>Net return</th><th>Vol.</th><th>Net Sharpe</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Original</th><td>12.32%</td><td>8.39%</td><td>1.43</td><td>28.2×</td></tr>
    <tr><th scope="row">PCA control</th><td>12.22%</td><td>8.33%</td><td>1.43</td><td>28.0×</td></tr>
    <tr><th scope="row">PCA 10%</th><td>12.21%</td><td>8.32%</td><td>1.43</td><td>28.0×</td></tr>
    <tr><th scope="row">Sector 20%</th><td>12.40%</td><td>8.40%</td><td>1.43</td><td>28.2×</td></tr>
    <tr><th scope="row">Sector 15%</th><td>12.30%</td><td>8.40%</td><td>1.42</td><td>28.3×</td></tr>
    <tr><th scope="row">Stock 4%</th><td>12.34%</td><td>8.42%</td><td>1.42</td><td>28.3×</td></tr>
    <tr><th scope="row">Stock 3%</th><td>12.30%</td><td>8.44%</td><td>1.42</td><td>28.4×</td></tr>
    <tr><th scope="row">Stock 2%</th><td>12.26%</td><td>8.47%</td><td>1.41</td><td>28.7×</td></tr>
    <tr class="period-heading"><th colspan="5">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Original</th><td>7.99%</td><td>9.32%</td><td>0.87</td><td>24.6×</td></tr>
    <tr><th scope="row">PCA control</th><td>8.11%</td><td>9.32%</td><td>0.88</td><td>24.5×</td></tr>
    <tr><th scope="row">PCA 10%</th><td>8.12%</td><td>9.30%</td><td>0.88</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector 20%</th><td>8.18%</td><td>9.29%</td><td>0.89</td><td>24.6×</td></tr>
    <tr><th scope="row">Sector 15%</th><td>8.17%</td><td>9.24%</td><td>0.89</td><td>24.7×</td></tr>
    <tr><th scope="row">Stock 4%</th><td>8.11%</td><td>9.31%</td><td>0.88</td><td>24.6×</td></tr>
    <tr><th scope="row">Stock 3%</th><td>8.30%</td><td>9.32%</td><td>0.90</td><td>24.7×</td></tr>
    <tr><th scope="row">Stock 2%</th><td>8.60%</td><td>9.30%</td><td>0.93</td><td>24.9×</td></tr>
  </tbody>
</table>

The caps gain little historically, but reducing the modeled concentration also
costs little. With the 7% forecast target, realized
volatility remains near 8.4% before 2022 and 9.3% afterward.

I also tried a 10% sector cap, but only one schedule completed before the next
hit the solver's iteration limit, so I stopped that test.

The 2% stock cap looks better if I focus on the later period: net Sharpe rises
from 0.87 to 0.93 and maximum drawdown falls from 9.05% to 8.47%. But the gain
is uneven across schedules, and over four years fixed schedules routinely
differ by more than that. Before 2022 the same cap lowers Sharpe, raises
turnover by about 0.55 times capital a year, and costs about 0.7 points in the
technology unwind (March 2000–October 2002) and 1.1 points around the
financial crisis (July 2007–June 2009). I can't distinguish the later gain from
rebalance-timing noise, so I wouldn't add it.

## What happens to the other risks?

A risk cap shouldn't quietly remove the strategy's intended low-volatility
tilt, which can span several principal components. As a simple check, I look at
whether the shorts are still more volatile than the longs.
For each book, I take the geometric mean of stock forecast volatility, weighted
by each position's share of that book's absolute weights.
The short-to-long ratio is 1.58 before 2022 and
1.75 later under the original optimizer; under the 10% PCA cap it is unchanged
at 1.58 and 1.75, and under the 2% stock cap 1.56 and 1.73. The intended
low-volatility tilt remains clear. This ratio
compares the stocks' volatilities; measuring how much portfolio risk comes from
that tilt would require factor attribution.

## Would I add these limits?

The weight limits leave some concentration, and since about 2015 it has sat
increasingly in a few leading components that cut across sectors. A 10% cap on every
component's share removes it with almost no change in return, Sharpe or
turnover, which makes it the only limit here I'd consider. Adopting it would
also mean switching the optimizer to the eligible-universe covariance, and that
switch alone moves targets by about 8–10% of capital, more than the cap itself.
Tighter sector caps and stock caps of 2–3% reshape the book without a benefit I
can distinguish from noise.

What I still don't know is what those leading components are. If the third and
fourth components since 2022 turn out to be the AI trade, a cap on shared risk
is the right tool; if they are a style exposure the ranking relies on, capping
them would cost more than it shows here.
