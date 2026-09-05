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

<p class="article-summary">A three-week strategy need not depend on one starting week. Splitting strategy notional into three equal sleeves and rebalancing one each week reduces that calendar choice. Here it lowers volatility by about 8% in development and 5% later, improving Sharpe in both periods. The sleeves still share most of their risk.</p>

## The starting-week problem

A strategy that rebalances every three weeks has three possible starting
weeks. Even with the same forecasting and allocation rules, each schedule
sees a different sequence of signals and prices. After 2021, annualized net
geometric return ranges from 5.42% to 9.91% across the three schedules in this
study. Choosing the best one after seeing those results would turn an
implementation detail into another backtest selection decision.

This revised study draws on [Newfound’s work on timing luck](https://blog.thinknewfound.com/2018/01/quantifying-timing-luck/)
and [Concretum’s study of tranching in factor portfolios](https://concretumgroup.com/the-tranching-dilemma-a-cost-aware-approach-to-mitigate-rebalance-timing-luck-in-factor-portfolios/).

I use a Ridge stock ranking with a constrained optimizer, a rank buffer for
existing holdings and a penalty on trading. The universe is point-in-time
Russell 1000 membership. Each schedule uses next-close execution and pays
5 bp per dollar traded. Only its starting week changes. The saved Ridge score
includes a range predictor that omits downward overnight gaps; these schedules
have not been rerun with its correction.

## Three sleeves

Each sleeve receives one third of strategy notional, holds its own portfolio
and continues to rebalance every three weeks. The backtest keeps that notional
fixed and lets weights drift between trades. I combine daily normalized P&L
across sleeves and compound that series into the displayed performance index.
A funded account replay would also need reinvestment, financing and borrow
assumptions. One sleeve trades each week:

<p class="table-caption"><strong>Table 1: Three staggered sleeves.</strong> Sleeve A, B and C each receive one third of strategy notional. The combined strategy trades weekly; each sleeve retains its three-week cycle.</p>

|  | Week 1 | Week 2 | Week 3 | Week 4 |
|---|---|---|---|---|
| Single schedule | Rebalance all | — | — | Rebalance all |
| Three sleeves | Rebalance A | Rebalance B | Rebalance C | Rebalance A |
{: .research-table .schedule-table }

This spreads notional over all three starting weeks without forecasting which
one will work best. It preserves the holding cycle within each sleeve while
making the overall portfolio less dependent on one calendar.

## The combined portfolio

Figure 1 shows the three schedules and their three-sleeve mixture from 2022
onward. The starting week makes a visible difference: the same strategy follows
three distinct paths. Combining the schedules spreads that timing risk while
retaining their shared gains and losses.

<div class="research-figure rebalancing-figure">
  {% include theme-svg-figure.html base="/assets/tranching/schedule-performance" version="2" alt="Net performance index from 2022 to May 2026 for three rebalance schedules and their three-sleeve mixture" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth from January 2022 through 27 May 2026, on a log scale. The bold line compounds the average daily return of the three schedules. This later period has already informed research choices.</p>

For daily net P&L per unit of fixed notional $r_{j,t}$, the combined series is

$$
r_{\mathrm{mix},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

Its arithmetic mean return equals the mean of the sleeves' arithmetic returns.
Volatility, Sharpe, geometric return and drawdown must be recomputed from this
combined daily series. Averaging three standalone Sharpes summarizes three
backtests; it does not give the Sharpe of the combined daily series.

Table 2 makes that distinction explicit. In development, mixture volatility
falls from the mean standalone 8.40% to 7.72%, and Sharpe rises from 1.43 to 1.55.
Later, volatility falls from 9.32% to 8.83% and Sharpe rises from 0.87 to 0.92.
Net geometric return changes little, while maximum drawdown also improves
relative to the mean standalone statistic.

<table class="research-table comparison-table">
  <caption><strong>Table 2: Combining the three schedules.</strong> Mean standalone statistics versus statistics recomputed from the combined daily returns on matched dates. Annualization uses 252 sessions and a zero cash rate. Each standalone maximum drawdown belongs to that schedule's own worst episode.</caption>
  <thead><tr><th>Period / construction</th><th>Gross geometric return</th><th>Net geometric return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr><th scope="row">Development · mean standalone</th><td>13.91%</td><td>12.31%</td><td>8.40%</td><td>1.43</td><td>−18.06%</td></tr>
    <tr><th scope="row">Development · three-sleeve mixture</th><td>13.97%</td><td>12.37%</td><td>7.72%</td><td>1.55</td><td>−15.53%</td></tr>
    <tr><th scope="row">Later · mean standalone</th><td>9.33%</td><td>7.99%</td><td>9.32%</td><td>0.87</td><td>−9.05%</td></tr>
    <tr><th scope="row">Later · three-sleeve mixture</th><td>9.36%</td><td>8.02%</td><td>8.83%</td><td>0.92</td><td>−8.83%</td></tr>
  </tbody>
</table>

## What improves, and what remains

Pairwise daily return correlations are around 0.76–0.77 in development and
0.84–0.85 later. The schedules therefore share most of their variation. Combining
them reduces timing risk, but a rally in common short holdings can still hurt
all three sleeves together. The later mixture still has an 8.83% drawdown.

Allocating one third of notional to each sleeve also incurs one third of its
proportional trading costs. Annual arithmetic cost drag is the mean of the
sleeves' costs: about 1.41 percentage points in development and 1.24 later.
This assumes separate sleeve trades, with no netting savings or fixed ticket
charges. More weekly trade events need not mean more traded notional.

I would fund all three sleeves. The evidence supports less dependence on the
starting week and a measured improvement in risk-adjusted performance, using
the same strategy. It does not remove the common exposures behind the remaining
drawdowns. Other weekdays or holding periods would be separate calendar tests.
