---
layout: post
title: "Combining Rebalance Weeks Reduces Timing Risk"
description: "Three equal sleeves reduce dependence on the starting week and improve risk-adjusted performance."
date: 2025-05-10
last_modified_at: 2026-09-05
categories: ["Rebalancing"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
series_previous: /quants/2026/09/05/risk-concentration.html
series_end: true
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/rebalance-tranching
---

<p class="article-summary">A three-week strategy need not depend on one starting week. Splitting strategy notional into three equal sleeves and rebalancing one each week reduces that calendar choice. Here it lowers volatility by about 8% in development and 5% later, improving Sharpe in both periods. The sleeves still share most of their risk.</p>

## The starting-week problem

“Rebalance every three weeks” sounds like a complete rule. It still leaves me
with a choice of three starting weeks. Each one sees a different sequence of
signals and prices, even though I use the same forecasting and allocation
rules. After 2021, annualized net
geometric return ranges from 5.42% to 9.91% across the three schedules in this
study. That is a lot to leave to the calendar. Choosing the best week after
seeing the results would just give me another way to fit the backtest.

This study draws on [Newfound’s work on timing luck](https://blog.thinknewfound.com/2018/01/quantifying-timing-luck/)
and [Concretum’s study of tranching in factor portfolios](https://concretumgroup.com/the-tranching-dilemma-a-cost-aware-approach-to-mitigate-rebalance-timing-luck-in-factor-portfolios/).

I take the [same stock strategy](/quants/2026/08/29/portfolio-optimization.html)
and run it from each of the three starting weeks. The ranking, sizing and
trading assumptions stay the same. I then split the strategy across all three
schedules instead of choosing one.

## Three sleeves

Each sleeve receives one third of strategy notional, holds its own portfolio
and continues to rebalance every three weeks. One sleeve trades each week:

<table class="research-table sleeve-schedule">
  <caption><strong>Table 1: Two rotations over six weeks.</strong> W1–W6 denote weeks; ● marks a rebalance and — means hold.</caption>
  <thead><tr><th>Sleeve</th><th>W1</th><th>W2</th><th>W3</th><th>W4</th><th>W5</th><th>W6</th></tr></thead>
  <tbody>
    <tr class="sleeve-a"><th scope="row">A <small>⅓ notional</small></th><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td></tr>
    <tr class="sleeve-b"><th scope="row">B <small>⅓ notional</small></th><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td></tr>
    <tr class="sleeve-c"><th scope="row">C <small>⅓ notional</small></th><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td></tr>
  </tbody>
</table>

I no longer need to choose a winning starting week. Each sleeve keeps the same
three-week holding cycle, and the overall portfolio participates in all three
schedules. Trading one sleeve each week is enough; I don't need to replace the
whole portfolio weekly.

## The combined portfolio

Figure 1 shows the three schedules and their three-sleeve mixture from 2022
onward. The starting week makes a visible difference: the same strategy follows
three distinct paths. Combining the schedules spreads that timing risk while
retaining their shared gains and losses.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/schedule-performance" mobile="/assets/tranching/schedule-performance_mobile" version="3" alt="Net performance index from 2022 to May 2026 for Sleeves A, B and C and their three-sleeve mixture" %}
</div>

<p class="figure-caption"><strong>Figure 1: Combining starting weeks reduces schedule dependence.</strong> Net growth index, January 2022–27 May 2026, on a log scale. The bold line compounds average daily P&amp;L. Paths retain their own volatilities; Table 2 compares risk as well as return. This later period has informed research choices.</p>

For daily net P&L per unit of fixed notional $r_{j,t}$, the combined series is

$$
r_{\mathrm{mix},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

Its arithmetic mean return equals the mean of the sleeves' arithmetic returns.
For volatility, Sharpe, geometric return and drawdown, I have to go back to the
combined daily series. What matters is whether the sleeves gain and lose on
the same days. Averaging three standalone Sharpes throws away that information.

Table 2 makes that distinction explicit. In development, mixture volatility
falls from the mean standalone 8.40% to 7.72%, and Sharpe rises from 1.43 to 1.55.
Later, volatility falls from 9.32% to 8.83% and Sharpe rises from 0.87 to 0.92.
Net geometric return changes little, while maximum drawdown also improves
relative to the mean standalone statistic.

<table class="research-table comparison-table">
  <caption><strong>Table 2: Combining the three schedules.</strong> Mean standalone statistics versus the combined daily series on matched dates. Net return is geometric, after 5 bp trading costs; annualization uses 252 sessions and Sharpe a zero cash rate. Drawdowns refer to each construction's own worst episode.</caption>
  <thead><tr><th>Construction</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Mean standalone</th><td>12.31%</td><td>8.40%</td><td>1.43</td><td>−18.06%</td></tr>
    <tr class="selected-rule"><th scope="row">Three-sleeve mixture</th><td>12.37%</td><td>7.72%</td><td>1.55</td><td>−15.53%</td></tr>
    <tr class="period-heading"><th colspan="5">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Mean standalone</th><td>7.99%</td><td>9.32%</td><td>0.87</td><td>−9.05%</td></tr>
    <tr class="selected-rule"><th scope="row">Three-sleeve mixture</th><td>8.02%</td><td>8.83%</td><td>0.92</td><td>−8.83%</td></tr>
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
charges. I send trades more often, but each sleeve is only a third of the size.

There is a small operational trade-off. I would need to track three sets of
holdings and rebalance dates, reconcile each sleeve, and run trades every week.
That is more bookkeeping than maintaining a single schedule, even when total
traded notional stays the same.

I would fund all three sleeves. I get the same strategy with less riding on
the starting week, and the combined portfolio has better Sharpe in both
periods. For me, that is worth the extra bookkeeping. Other weekdays or holding
periods would be separate calendar tests.

## Research notes

The linked allocation study gives the ranking, universe and sizing rules.
Each schedule executes at the next close and pays 5 bp per dollar traded.
The backtest keeps strategy notional fixed and lets weights drift between
trades. The displayed index compounds average daily P&L per unit of notional;
a funded account replay would also need reinvestment, financing and borrow
assumptions.
