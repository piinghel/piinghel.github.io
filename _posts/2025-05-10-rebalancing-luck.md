---
published: false
layout: post
interactive_charts: true
toc: true
title: "Reducing Rebalancing Luck"
description: "Combining Ridge rebalance schedules preserves mean return while reducing volatility and the risk of choosing an unlucky starting week."
date: 2025-05-10
last_modified_at: 2026-10-02
categories: ["Portfolio construction"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/rebalance-tranching
---

My [Ridge strategy](/quants/2025/02/09/multiple-linear-regression.html)
rebalances every three weeks. That leaves a small decision: which three
weeks? I could start this Friday, next Friday, or the Friday after. The model
is the same in each case, but the portfolios won't be. A stock can move a
long way in the week between two rebalances.

In the other articles I report results across three starting weeks. Here I
combine them, with one third of the portfolio in each. The idea is
diversification: preserve the mean return across schedules, lower volatility,
and improve Sharpe. It also reduces the risk of choosing the starting week
that happens to do badly.

[Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck)
and [Concretum's tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
use this approach to reduce rebalance timing risk. I want to see how much
it helps my Ridge strategy, and what it means for trading.

## The starting week matters

Figure 1 shows the three Friday schedules from January 2022 to May 2026.
They use the same Ridge regression on 80 ranking predictors and the same
[joint sizing rules](/quants/2026/08/29/portfolio-optimization.html),
including the rank buffer and trade penalty. Each schedule holds its own
book and trades every three weeks, at the close after its signal date.
All returns include 5 bp per dollar traded.

Over this period, annualized net return ranges from **5.73% to 8.95%**.
That is a 3.22 percentage point gap from choosing a different starting
week. Had I picked Week 3, I would have ended up with 5.73%. Combining the
three gives **7.70%**: I give up the best calendar's result, but also avoid
putting the whole portfolio into the worst one.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="schedules" source="/assets/tranching/ridge-paths.json?v=1" base="/assets/tranching/ridge-paths" mobile="/assets/tranching/ridge-paths_mobile" label="Net growth of three Friday rebalance schedules and their equal-notional combination, January 2022 to May 2026." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 1: Less dependence on one starting week.</strong> Friday signal schedules, January 2022–May 2026, indexed to 100 at the 31 December 2021 close. Grey lines show the individual schedules; blue combines them at one third of notional each. Each line compounds daily net P&amp;L per unit of fixed notional. Explore gives access to the longer history.</p>

The choice of weekday adds another dimension. Monday through Friday, each
with three starting weeks, gives fifteen calendars. Holidays move the
scheduled signal to the next eligible session.

The allocator uses 21-session stock volatility, a 7% forecast portfolio
volatility budget and a 2.0 gross exposure cap.[^calibration] I report
September 1998–December 2021 and January 2022–May 2026 separately.

## Split the portfolio across three weeks

I don't have to choose one starting week. I can give each one a third of
the strategy's notional and keep the three books separate. Each still
rebalances every three weeks, but one of them trades each week (Table 1).
This spreads the timing of portfolio changes while preserving each book's
holding period.

<table class="research-table sleeve-schedule">
  <caption><strong>Table 1: Three books, one rebalance each week.</strong> W1–W6 denote weeks; ● marks a rebalance and — means hold.</caption>
  <thead><tr><th>Offset</th><th>W1</th><th>W2</th><th>W3</th><th>W4</th><th>W5</th><th>W6</th></tr></thead>
  <tbody>
    <tr class="sleeve-a"><th scope="row">Week 1 <small>⅓ notional</small></th><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td></tr>
    <tr class="sleeve-b"><th scope="row">Week 2 <small>⅓ notional</small></th><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td></tr>
    <tr class="sleeve-c"><th scope="row">Week 3 <small>⅓ notional</small></th><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td></tr>
  </tbody>
</table>

For daily net P&L per unit of fixed notional $$r_{j,t}$$, the combined
return is simply

$$
r_{\mathrm{combined},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

Its arithmetic mean is exactly the average of the three schedules' means,
costs included. Compounding those averaged daily returns need not give the
average of the three compounded returns. I keep the same total notional throughout;
I don't scale the combined portfolio back up to recover any reduction in
volatility.

## The diversification benefit

The books diversify each other. They often hold the same stocks, but
they entered them at different dates and carry different weights between
rebalances. Their daily returns are closely correlated without being
identical.

Average volatility falls from **8.75% to 8.15%** in development and from
**9.65% to 9.26%** later (Table 2), reductions of 6.9% and 4.1%. The smaller
later benefit fits the higher correlation between the books: 0.88 on
average, against 0.80 in development. Sharpe rises from **1.30 to 1.40** in
development and from **0.81 to 0.84** later. That is the expected diversification benefit: the same
arithmetic mean return with less daily variability. The small differences
in compounded return reflect compounding. Average drawdowns also improve,
though more modestly.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Diversification improves Sharpe.</strong> Mean of each statistic across fifteen single schedules or five three-tranche portfolios. Returns are geometric; return, volatility and drawdown are percentages. Annualization uses 252 sessions and Sharpe a zero cash rate.</caption>
  <thead><tr><th>Metric</th><th>Single<br>schedule</th><th>Three<br>tranches</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">September 1998–December 2021</th></tr>
    <tr><th scope="row">Net return</th><td>11.67</td><td>11.73</td></tr>
    <tr><th scope="row">Volatility</th><td>8.75</td><td>8.15</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.30</td><td>1.40</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−18.48</td><td>−17.50</td></tr>
    <tr class="period-heading"><th colspan="3">January 2022–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>7.62</td><td>7.66</td></tr>
    <tr><th scope="row">Volatility</th><td>9.65</td><td>9.26</td></tr>
    <tr><th scope="row">Sharpe</th><td>0.81</td><td>0.84</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−9.85</td><td>−9.64</td></tr>
  </tbody>
</table>

Lower volatility also gives a choice: keep the smoother portfolio, or
increase exposure to bring risk back toward the original level. Scaling
would raise expected return and volatility together; the better Sharpe
comes from diversification. Here I keep total notional unchanged. Using
more leverage would also have to fit the gross exposure and other
portfolio limits, with financing costs included.

## Less dependence on the calendar

Figure 2 puts all fifteen schedules on the same return scale. Each row
shows one signal weekday: the three small symbols are the starting weeks,
and the diamond combines them. There are therefore fifteen single schedules
and five combined portfolios in each panel.

The return spread falls from **2.65 to 1.26 percentage points** in the
development period, and from **3.77 to 0.95 points** later. The combined
portfolios are closer together, although the choice of weekday still
makes a difference.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="calendars" source="/assets/tranching/ridge-calendars.json?v=1" base="/assets/tranching/ridge-calendars" mobile="/assets/tranching/ridge-calendars_mobile" label="Annualized net returns for fifteen single calendars and five three-tranche portfolios in 1998–2021 and 2022–May 2026, on a common scale." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 2: Combining starting weeks leaves the weekday choice.</strong> Annualized geometric net return, with the same horizontal scale in both periods. Circles, squares and triangles identify the three starting weeks; diamonds combine them at one third of notional each. The thin lines span the three observed schedule returns within a weekday.</p>

The comparison across fifteen singles and five combinations removes one
calendar choice by construction. A closer comparison holds the starting
week fixed and asks how much returns vary across the five weekdays.

In development, the weekday spreads for Weeks 1, 2 and 3 are 1.03, 1.69
and 2.56 points. The combined portfolio's 1.26-point spread is smaller than
two of those, but larger than the first. Later, its 0.95-point spread is
smaller than all three: 1.34, 3.30 and 3.69 points. Tranching helps across
the full grid, without dominating every individual starting-week comparison.
## Putting the spread in context

A calendar that wins in a backtest could have a persistent advantage. It
could also have happened to trade before favourable moves. To put the
observed spread in context, I use a resampling test where all fifteen
calendars have the same arithmetic mean return.

I remove each calendar's mean and add back their common mean, then resample
63-session blocks of days. I draw the same blocks for every calendar, which
preserves their dependence on one another and much of the variation within
each quarter. For each of 2,000 draws, I calculate the gap between the
highest and lowest compounded annual return.

In development, the simulated spread is at least as large as the observed
2.65 points in **48%** of draws. Later, it exceeds the observed 3.77 points
in **87%** of draws. Neither spread is unusually large under this model.
Across 21-, 63- and 126-session blocks, those frequencies are 45–55% in
development and 87–90% later.

This is a check on how surprising the spread is under that model. It
doesn't establish that all schedules have the same expected return.
Combining schedules is useful when I don't have a reason, available in
advance, to prefer the one that happened to win.

## More orders, similar traded notional
{: #what-it-takes-to-implement }

Splitting the portfolio changes the shape of the trading. Each tranche
trades less, but I have three of them. At equal total notional, their traded
notional averages to that of the individual schedules, while their order
counts add up. Here, two-way turnover means purchases plus sales divided by
strategy notional.

Over the later period, a single schedule averages about **2,429 orders a
year**, against **7,288** for three tranches. Two-way turnover averages
**18.83 times notional a year** in both cases. At USD 5 million total
notional, that means an average order of roughly USD 38,800 for one
schedule and USD 12,900 for three tranches.

The proportional cost deduction is therefore the same: **0.94 percentage
points a year** later and **1.29 points** in development, measured as the
annualized average of daily costs. Splitting the orders doesn't make that
5 bp charge cheaper, but it doesn't increase it either.

For this comparison I scale the trades of each USD 5 million standalone
book to one third of their size. I allow fractional quantities, charge
costs before any netting between books, and don't re-optimize or round
orders for the smaller tranches. Fixed ticket charges, borrow, financing
and market impact are outside the calculation.

That matters for interpreting the benefit. Zarattini and Pagani's
[tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
also finds that spreading rebalance dates reduces variation across
schedules while leaving average returns broadly similar. Their cost
analysis shows why the answer can change with portfolio size: smaller
orders can reduce impact, but minimum commissions can make the extra
tickets expensive.

## What I would keep

I would keep the three starting weeks. They give the Ridge portfolio a
better Sharpe without changing its arithmetic mean return, and make the
outcome less dependent on picking a fortunate calendar. I don't need to
find the week that earns 8.95%; I also don't want the whole portfolio stuck
with the one that earns 5.73%.

The combined portfolio lets me take that diversification benefit as lower
volatility, or potentially as more exposure at a chosen risk level. At the
same notional and proportional costs used here, I prefer its smoother
returns and reduced dependence on the starting date.

## References

- Corey Hoffstein, Justin Sibears and Nathan Faber, *Rebalancing Timing Luck: The Difference between Hired and Fired*, summarized in [Newfound Research's rebalance timing luck overview](https://www.thinknewfound.com/rebalance-timing-luck).
- Carlo Zarattini and Alberto Pagani, [*The Tranching Dilemma: A Cost-Aware Approach to Mitigate Rebalance Timing Luck in Factor Portfolios*](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf), 14 November 2025 version, PDF pp. 9–12.

[^calibration]: Stock-volatility estimates are multiplied by 1.18 here, compared with 1.55 in the joint-sizing article. All fifteen calendars use the same multiplier.
