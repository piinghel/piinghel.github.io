---
layout: post
title: "Combining Rebalance Weeks Reduces Timing Risk"
description: "Averaging schedule statistics improves reporting; combining daily returns also reduces portfolio risk."
date: 2025-05-10
last_modified_at: 2026-09-05
categories: ["Rebalancing"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
series_previous: /quants/2026/08/29/portfolio-optimization.html
series_end: true
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">A strategy that rebalances every three weeks can look quite different depending on its starting week. Splitting capital across all three weeks avoids choosing one calendar and reduces volatility by about 8% in development and 5% later for this Ridge strategy. Most of the risk remains because the three portfolios tend to gain and lose together.</p>

## Averaging results or combining portfolios?

The [portfolio-optimization article](/quants/2026/08/29/portfolio-optimization.html)
compares construction rules using the mean of three schedule-level statistics.
One schedule trades in weeks 1, 4, 7, and so on; another in weeks 2, 5, 8; the
third in weeks 3, 6, 9. Reporting their mean makes the comparison less dependent
on a convenient starting date.

Averaging the three Sharpe ratios summarizes those separate backtests. To
measure the portfolio I would actually trade, I need to divide the capital
between the schedules and combine their daily returns.

I use the Ridge ranking and constrained optimizer with trading controls
from that article. The universe, forecasts, sizing rule, and cost convention are
unchanged. A *sleeve* is one of those schedule-specific
portfolios, funded with its share of the total fixed notional.

All comparisons use matched dates: 22 September 1998–31 December 2021 for
development, and 3 January 2022–27 May 2026 for the later period. The latter has
already informed research choices elsewhere in this series. The comparison
covers three starting weeks, with forecasts updated on each rebalance date.
Different weekdays would require additional backtests.

Matching the three starts drops a few early September observations used by the
first two schedules in the optimization tables, explaining the small difference
in development means.

## Combining daily returns

After 2021, annualized net geometric return ranges from 5.42% to 9.91% across
the three starting weeks. Choosing
one schedule after seeing that spread would turn an implementation detail into
a backtest selection rule. The mixture avoids that choice without needing to
predict which week will work best next.

If $$r_{j,t}$$ is daily net P&L per unit of fixed
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
clearer reduction in volatility, using the same forecasts.

<table class="research-table comparison-table">
  <thead><tr><th>Period / construction</th><th>Gross geometric return</th><th>Net geometric return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr><th scope="row">Development · mean standalone</th><td>13.91%</td><td>12.31%</td><td>8.40%</td><td>1.43</td><td>−18.06%</td></tr>
    <tr><th scope="row">Development · three-sleeve mixture</th><td>13.97%</td><td>12.37%</td><td>7.72%</td><td>1.55</td><td>−15.53%</td></tr>
    <tr><th scope="row">Later · mean standalone</th><td>9.33%</td><td>7.99%</td><td>9.32%</td><td>0.87</td><td>−9.05%</td></tr>
    <tr><th scope="row">Later · three-sleeve mixture</th><td>9.36%</td><td>8.02%</td><td>8.83%</td><td>0.92</td><td>−8.83%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Mean statistics across three standalone schedules versus statistics recomputed after averaging their daily returns. Annualization uses 252 sessions and a zero cash rate. Each standalone drawdown is measured over that schedule's own worst episode.</p>

## Timing dispersion and diversification

[Concretum's *The Tranching Dilemma*](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
makes the calendar problem visual by plotting the spread in geometric returns
as more schedules are combined. Its monthly momentum experiment also
distinguishes rising trade counts from broadly unchanged funded turnover.
Its strategy, schedule grid, and costs differ from mine; I use its framing to
examine the three schedules here.

Figure 1 shows what happens as I fund more starting weeks. The top row tracks
the spread in return across the possible combinations. The bottom row shows
their volatility. These are two different benefits: less dependence on one
calendar and less variation in daily P&L.

<div class="research-figure rebalancing-figure">
  {% include theme-svg-figure.html base="/assets/tranching/timing-dispersion" version="2" alt="Return spread narrows as starting weeks are combined; the all-three mixture reduces volatility by 8.1 percent in development and 5.3 percent later" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> All seven combinations: three individual weeks, three pairs, and all three weeks. Segments connect the lowest and highest values at each sleeve count. Return scales differ by period; volatility uses a common scale. Dashed lines mark mean single-schedule volatility. Results include the 5 bp trading charge. <a href="/assets/tranching/timing_metrics.csv">Data</a> · <a href="https://github.com/piinghel/piinghel.github.io/blob/main/scripts/render_timing_figure.py">Figure code</a>.</p>

Using two sleeves narrows the observed spread in both periods. At three sleeves,
the spread is zero because there is only one combination left.
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

For intuition, three equally volatile sleeves with pairwise correlation of
0.85 have mixture volatility of about 95% of a single sleeve's volatility.
Three schedules provide much less diversification than three independent bets.

Tranching diversifies differences between the schedules; their common exposures
remain. That is why the later-period volatility reduction is modest even
though the starting-week choice disappears. It also leaves the roughly 9%
drawdown discussed in the optimization article: the short holdings can still
rally together across all three schedules.

## Trading costs

Each schedule pays five basis points per unit of executed absolute weight
change, including exits. Giving it one third of the total notional also gives
it one third of the total cost contribution. The mixture's annual arithmetic
cost drag is therefore exactly the mean of the three sleeves' cost drags:
about 1.41 percentage points in development and 1.24 points later. Adding
sleeves spreads that proportional cost across the funded portfolios.

This calculation preserves the separate sleeve trades. It assumes no savings
from netting opposing orders across sleeves and adds no fixed charge per
ticket. An implementation could have more trade tickets without more funded
turnover. Minimum fees, spread, market impact, borrow, and financing would need
their own estimates before assessing capacity or choosing an operational schedule.

## How I would rebalance

I would fund the three schedules and keep reporting their standalone results
alongside the mixture. That makes the implementation less dependent on one
starting week and keeps its calendar sensitivity visible.

The next useful question is why all three sleeves lose money together. P&L
attribution alongside risk decomposition would help distinguish a common
exposure from stock-specific losses, especially through the short-book
drawdowns in the [optimizer study](/quants/2026/08/29/portfolio-optimization.html).
