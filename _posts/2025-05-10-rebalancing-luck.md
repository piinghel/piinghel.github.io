---
layout: post
title: "Combining Rebalance Weeks Reduces Timing Risk"
description: "Three equal sleeves reduce dependence on the starting week and improve risk-adjusted performance."
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

<p class="article-summary">A three-week strategy need not depend on one starting week. Funding three equal sleeves and rebalancing one each week reduces that calendar choice. Here it lowers volatility by about 8% in development and 5% later, improving Sharpe in both periods. The sleeves still share most of their risk.</p>

## The starting-week problem

A strategy that rebalances every three weeks has three possible starting
weeks. Even with the same forecasting and allocation rules, each schedule
sees a different sequence of signals and prices. After 2021, annualized net
geometric return ranges from 5.42% to 9.91% across the three schedules in this
study. Choosing the best one after seeing those results would turn an
implementation detail into another backtest selection decision.

I use a Ridge stock ranking with a constrained optimizer, a rank buffer for
existing holdings and a penalty on trading. The universe is point-in-time
Russell 1000 membership. Each schedule uses next-close execution and pays
5 bp per dollar traded. Only its starting week changes.

## Three sleeves

I divide the capital equally between the three schedules. Each sleeve receives
one third of the total, holds its own portfolio and continues to rebalance
every three weeks. One sleeve trades each week:

|  | Week 1 | Week 2 | Week 3 | Week 4 |
|---|---|---|---|---|
| Single schedule | Rebalance all | — | — | Rebalance all |
| Three sleeves | Rebalance A | Rebalance B | Rebalance C | Rebalance A |
{: .research-table .schedule-table }

<p class="table-caption"><strong>Table 1:</strong> Sleeve A, B and C each receive one third of capital. The combined strategy trades weekly; each sleeve retains its three-week cycle.</p>

This spreads capital over all three starting weeks without forecasting which
one will work best. It preserves the holding cycle within each sleeve while
making the overall portfolio less dependent on one calendar.

## The combined portfolio

Figure 1 compares the three schedules with their equal-funded mixture. Each
panel starts at one, so the later-period differences are visible separately
from the long development history. The mixture participates in the schedules'
shared gains and losses while spreading their timing differences.

<div class="research-figure rebalancing-figure">
  {% include theme-svg-figure.html base="/assets/tranching/schedule-performance" version="1" alt="Net growth of one dollar for three rebalance schedules and their equal-funded mixture, shown separately for development and later history" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Compounded net daily P&amp;L per unit of fixed notional, with a log scale in each panel. The bold line combines daily returns before compounding. Development runs from 22 September 1998 through December 2021; later history runs from January 2022 through 27 May 2026 and has already informed research choices. Panel scales differ.</p>

For daily net P&L per unit of fixed notional $r_{j,t}$, the combined series is

$$
r_{\mathrm{mix},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

Its arithmetic mean return equals the mean of the sleeves' arithmetic returns.
Volatility, Sharpe, geometric return and drawdown must be recomputed from this
combined daily series. Averaging three standalone Sharpes summarizes three
backtests; it does not give the Sharpe of the funded mixture.

Table 2 makes that distinction explicit. In development, mixture volatility
falls from the mean standalone 8.40% to 7.72%, and Sharpe rises from 1.43 to 1.55.
Later, volatility falls from 9.32% to 8.83% and Sharpe rises from 0.87 to 0.92.
Net geometric return changes little, while maximum drawdown also improves
relative to the mean standalone statistic.

<table class="research-table comparison-table">
  <thead><tr><th>Period / construction</th><th>Gross geometric return</th><th>Net geometric return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr><th scope="row">Development · mean standalone</th><td>13.91%</td><td>12.31%</td><td>8.40%</td><td>1.43</td><td>−18.06%</td></tr>
    <tr><th scope="row">Development · three-sleeve mixture</th><td>13.97%</td><td>12.37%</td><td>7.72%</td><td>1.55</td><td>−15.53%</td></tr>
    <tr><th scope="row">Later · mean standalone</th><td>9.33%</td><td>7.99%</td><td>9.32%</td><td>0.87</td><td>−9.05%</td></tr>
    <tr><th scope="row">Later · three-sleeve mixture</th><td>9.36%</td><td>8.02%</td><td>8.83%</td><td>0.92</td><td>−8.83%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Mean standalone statistics versus statistics recomputed from the combined daily returns on matched dates. Annualization uses 252 sessions and a zero cash rate. Each standalone maximum drawdown belongs to that schedule's own worst episode.</p>

The simulations size against fixed notional and let weights drift between
trades. Compounding the normalized P&L gives a performance index; a funded
account replay would also need reinvestment, financing and borrow assumptions.

## What improves, and what remains

Pairwise daily return correlations are around 0.76–0.77 in development and
0.84–0.85 later. The schedules therefore share most of their variation. Combining
them reduces timing risk, but a rally in common short holdings can still hurt
all three sleeves together. The later mixture still has an 8.83% drawdown.

Funding each sleeve with one third of notional also funds one third of its
proportional trading costs. Annual arithmetic cost drag is the mean of the
sleeves' costs: about 1.41 percentage points in development and 1.24 later.
This assumes separate sleeve trades, with no netting savings or fixed ticket
charges. More weekly trade events need not mean more traded notional.

I would fund all three sleeves. The evidence supports less dependence on the
starting week and a measured improvement in risk-adjusted performance, using
the same strategy. It does not remove the common exposures behind the remaining
drawdowns. Other weekdays or holding periods would be separate calendar tests.
