---
layout: post
title: "What Averaging Rebalance Weeks Already Fixes"
date: 2025-05-10
last_modified_at: 2026-09-05
categories: ["Rebalancing"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
---

## Summary

A strategy that rebalances every three weeks still needs a starting week. I already report results across all three choices, which prevents one lucky calendar from representing the strategy. Allocating across those schedules goes a step further: it diversifies their daily P&L. In the current constrained Ridge portfolio, the three-sleeve mixture reduces volatility by about 8% in development and 5% in the later period. It removes the starting-week choice within this grid, but the sleeves remain strongly correlated. That distinction matters more to me than finding a supposedly optimal number of tranches.

## An average result is not an averaged portfolio

The [portfolio-optimization article](/quants/2026/08/29/portfolio-optimization.html)
compares construction rules using the mean of three schedule-level statistics.
Each schedule follows the same three-week cycle, shifted by one week. Reporting
their mean makes the comparison less dependent on a convenient starting date.

But averaging three Sharpe ratios does not give the Sharpe ratio of a portfolio
that holds all three schedules. The first operation summarizes an experiment;
the second changes the return stream. I wanted to check how much the second
operation buys when the first is already part of the research process.

I use the frozen Ridge ranking and constrained optimizer with trading controls
from that article. The universe, forecasts, sizing rule, and cost convention are
unchanged. This is a new aggregation of saved daily backtests, not a new model
fit or a search over rebalance dates. A *sleeve* is one of those schedule-specific
portfolios, funded with its share of the total fixed notional.

All comparisons use matched dates: 22 September 1998–31 December 2021 for
development, and 3 January 2022–27 May 2026 for the later period. The latter has
already informed research choices elsewhere in this series; it is reused
history, not an untouched holdout. Only three starting weeks are available in
this experiment. It does not test different weekdays or isolate execution
timing from the changing forecasts available on each rebalance date.

Matching the three starts here also drops a few early September observations
used by the first two schedules in the optimization tables. That accounts for
the small difference in their reported development means.

## The starting week still changes the path

Figure 1 shows the three standalone schedules as thin lines and their
equal-notional mixture in blue. Each panel starts a fresh compounded index.
The logarithmic axes show proportional changes; their ranges differ because
the development period is much longer.

<div class="research-figure rebalancing-figure">
  {% include theme-svg-figure.html base="/assets/tranching/timing-paths" version="1" alt="Three starting-week compounded net return paths and their equal-notional mixture, shown separately for development and the later period on logarithmic axes" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Starting-week paths and the three-sleeve mixture, after five-basis-point proportional trading costs. These are compounded indices of fixed-notional daily P&L, not financed account histories.</p>

The development paths finish fairly close together. In the shorter later
period, annualized net geometric return ranges from 5.42% to 9.91%. Choosing
one schedule after seeing that spread would turn an implementation detail into
a backtest selection rule. The mixture avoids that choice without needing to
predict which week will work best next.

The construction is explicit. If $$r_{j,t}$$ is daily net P&L per unit of fixed
notional for schedule $$j$$, then funding each with one third of the total gives

$$
r_{\mathrm{mix},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

The arithmetic mean return of this mixture equals the mean arithmetic return
of its sleeves. Geometric return, volatility, Sharpe, and drawdown must be
recomputed from the mixed daily series. In particular, compounding an average
daily return is different from averaging three separately compounded indices.
I use the former here. As elsewhere in the series, compounding is a performance
summary; the underlying simulations use fixed-notional sizing and floating
weights between rebalances.

Table 1 separates the mean standalone statistics from the statistics of the
actual return mixture. The small change in geometric return accompanies a
clearer reduction in volatility. It does not imply that tranching improved the
forecasts.

<table class="research-table comparison-table">
  <thead><tr><th>Period / construction</th><th>Gross geometric return</th><th>Net geometric return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr><th scope="row">Development · mean standalone</th><td>13.91%</td><td>12.31%</td><td>8.40%</td><td>1.43</td><td>−18.06%</td></tr>
    <tr><th scope="row">Development · three-sleeve mixture</th><td>13.97%</td><td>12.37%</td><td>7.72%</td><td>1.55</td><td>−15.53%</td></tr>
    <tr><th scope="row">Later · mean standalone</th><td>9.33%</td><td>7.99%</td><td>9.32%</td><td>0.87</td><td>−9.05%</td></tr>
    <tr><th scope="row">Later · three-sleeve mixture</th><td>9.36%</td><td>8.02%</td><td>8.83%</td><td>0.92</td><td>−8.83%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Mean statistics across three standalone schedules versus statistics recomputed after averaging their daily returns. Annualization uses 252 sessions and a zero cash rate. Mean standalone drawdown averages three separate worst episodes, not necessarily a common event.</p>

## What the shrinking dispersion does—and does not—show

[Concretum's *The Tranching Dilemma*](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
makes the calendar problem visual by plotting the spread in geometric returns
as more schedules are combined. Its monthly momentum experiment also
distinguishes rising trade counts from broadly unchanged funded turnover.
That is a useful way to frame the decision, though its strategy, schedule grid,
and cost assumptions differ from mine.

Figure 2 applies the dispersion idea to the available three-week grid. Each dot
is a distinct equal-notional combination: three individual schedules, three
pairs, and one mixture of all three. The vertical segment joins the lowest and
highest geometric return at each sleeve count. The panel scales differ so that
the much smaller development spread remains visible.

<div class="research-figure rebalancing-figure">
  {% include theme-svg-figure.html base="/assets/tranching/timing-dispersion" version="1" alt="All combinations of one, two, and three starting-week sleeves, showing the range of annualized net geometric returns separately in development and the later period" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Geometric-return dispersion across every subset of the three saved schedules. Dots are observed combinations, not independent trials or confidence intervals.</p>

Using two sleeves narrows the observed spread in both periods. At three sleeves,
the spread is zero because there is only one combination left. That endpoint
is a property of the grid, not evidence that timing risk in general has vanished.
Another weekday, holding period, or prediction-release convention could still
change the result.

The remaining portfolio risk is substantial. Pairwise daily return correlations
are around 0.76–0.77 in development and 0.84–0.85 later. With correlated sleeves,
the variance of their mixture is

$$
\operatorname{Var}(r_{\mathrm{mix}})
=\frac{1}{9}\sum_{i=1}^{3}\sum_{j=1}^{3}
\operatorname{Cov}(r_i,r_j).
$$

Tranching diversifies differences between the schedules; their common exposures
remain. That is why the later-period volatility reduction is modest even
though the starting-week choice disappears. It also leaves the roughly 9%
drawdown discussed in the optimization article. Splitting the rebalance cannot
be expected to repair a short book whose holdings rally together.

## Costs follow funded trades, not the number of sleeves

Each saved schedule pays five basis points per unit of executed absolute weight
change, including exits. Giving it one third of the total notional also gives
it one third of the total cost contribution. The mixture's annual arithmetic
cost drag is therefore exactly the mean of the three sleeves' cost drags:
about 1.41 percentage points in development and 1.24 points later. Adding
sleeves does not multiply that proportional cost by three.

This calculation preserves the separate sleeve trades. It assumes no savings
from netting opposing orders across sleeves and adds no fixed charge per
ticket. An implementation could have more trade tickets without more funded
turnover. Minimum fees, spread, market impact, borrow, and financing would need
their own estimates before choosing an operational schedule. These backtests
do not establish capacity or an optimal tranche count.

## I would keep the three-week coverage

Averaging across weeks already fixes a major reporting weakness: the strategy
is no longer represented by whichever starting week happens to look good.
Actually funding the three schedules adds a measurable, moderate reduction in
volatility. Both are worth keeping, and they answer different questions.

I would spend the next research effort on the risk shared by the sleeves rather
than on a larger calendar grid. The optimizer can control portfolio-level risk
without explaining which exposures paid for taking it. That calls for a P&L
attribution alongside the risk decomposition, especially through the short-book
drawdowns.

## Reproducibility and revision

The [aggregate metrics](/assets/tranching/timing_metrics.csv) include all seven
combinations in both periods. The
[manifest](/assets/tranching/timing_manifest.json) records conventions and hashes
of the three source return files. The calculation and SVG renderer live in
the research project's rebalance-timing module; licensed security-level data
are not distributed here.

This revision replaces an older LightGBM example whose retained archive lacked
daily returns, exact sample dates, and a complete cost record. Its figures and
tables remain in the site's Git history, but I no longer use them to support
the current portfolio's implementation choice.
