---
published: true
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
rebalances every three weeks. I still have to choose a starting date: this
Friday, next Friday, or the Friday after. The model is the same in each case,
but a week's difference in timing can leave me with quite different returns.

In the other articles I report results across three starting weeks. Here I
combine them, with one third of the notional in each. I want the
diversification benefit—lower volatility and a higher Sharpe ratio at the
same average return—and less dependence on picking a fortunate starting week.

[Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck)
and [Concretum's tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
discuss this approach to rebalance timing risk. Here I apply it to Ridge
and look at the benefit after trading costs.

## The starting week matters

Figure 1 shows the three Friday schedules from January 2022 to May 2026.
They use the same Ridge regression on 80 ranking predictors and the same
[joint sizing rules](/quants/2026/08/29/portfolio-optimization.html),
including the rank buffer and trade penalty.[^calibration] Each schedule
trades at the close after its signal date. All returns include 5 bp per
dollar traded.

Over this period, annualized net return ranges from **5.73% to 8.95%**.
That is a 3.22 percentage point gap from choosing a different starting
week. Combining the three gives **7.70%**. I couldn't have known in advance
which week would win, and I wouldn't want the whole portfolio exposed to
the one that earned 5.73%.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="schedules" source="/assets/tranching/ridge-paths.json?v=1" base="/assets/tranching/ridge-paths" mobile="/assets/tranching/ridge-paths_mobile" label="Net growth of three Friday rebalance schedules and their equal-notional combination, January 2022 to May 2026." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 1: Less dependence on one starting week.</strong> Friday signal schedules, January 2022–May 2026, indexed to 100 at the 31 December 2021 close. Grey lines show the individual schedules; blue combines them at one third of notional each. Each line compounds daily net P&amp;L per unit of fixed notional. Explore gives access to the longer history.</p>

## Split the portfolio across three weeks

I implement the combination as three separate books, or tranches, each
with one third of the strategy's notional. Each still rebalances every
three weeks, but one of them trades each week (Table 1). This spreads the
portfolio changes over time while preserving each book's holding period.

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
costs included. The small differences in geometric return come from
compounding the combined daily returns. I keep total notional unchanged
throughout the comparison.

## The diversification benefit

The three books use the same model at different dates, so their returns
are closely correlated without being identical. Averaging them reduces
volatility relative to the average standalone schedule.

To see how much this helps beyond Friday, I repeat the comparison for
every weekday. Three starting weeks across five weekdays give fifteen
single schedules and five combined portfolios. I report September
1998–December 2021, the development period, and January 2022–May 2026,
the later period, separately.

Table 2 shows the expected diversification benefit. Average volatility
falls from **8.75% to 8.15%** in development and from **9.65% to 9.26%**
later. Sharpe rises from **1.30 to 1.40** and **0.81 to 0.84**, respectively.
The smaller later benefit is consistent with the higher correlation between
starting weeks: 0.88 on average, against 0.80 in development. There is less
to diversify when the books move more closely together.

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

I could keep that reduction in volatility or use more leverage at the
same risk level. Proportional scaling would raise expected return and
volatility together, preserving the Sharpe improvement before additional
costs. The scope for doing so depends on the gross exposure and other
portfolio limits, as well as financing costs.

## Less dependence on the calendar

Lower daily volatility is one benefit; less dependence on the calendar
is the other. Figure 2 compares all fifteen schedules with the five
combined portfolios. Each row holds the signal weekday fixed, so I can
see how much the starting week changes the result.

The return spread falls from **2.65 to 1.26 percentage points** in the
development period, and from **3.77 to 0.95 points** later. The combined
portfolios are closer together, although the choice of weekday still
makes a difference.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="calendars" source="/assets/tranching/ridge-calendars.json?v=1" base="/assets/tranching/ridge-calendars" mobile="/assets/tranching/ridge-calendars_mobile" label="Annualized net returns for fifteen single calendars and five three-tranche portfolios in 1998–2021 and 2022–May 2026, on a common scale." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 2: Combining starting weeks leaves the weekday choice.</strong> Annualized geometric net return, with the same horizontal scale in both periods. Circles, squares and triangles identify the three starting weeks; diamonds combine them at one third of notional each. The thin lines span the three observed schedule returns within a weekday.</p>

Combining starting weeks leaves five calendars instead of fifteen. If I
instead fix one starting week and compare only the five weekdays, the
improvement is less uniform: Week 1 has a narrower spread than the
combination in development, 1.03 versus 1.26 points. Later, the combined
spread is smaller than for any fixed starting week. I reduce dependence
on the starting date, while retaining some weekday risk.

## Putting the spread in context

A calendar that wins in a backtest might have a persistent advantage.
Before preferring it, though, I want to know whether a gap this large is
unusual when the calendars have equal expected returns.

I equalize their arithmetic means and resample 63-session blocks of days,
using the same blocks for all fifteen calendars. This preserves their
dependence on one another and the sequence of returns within each block.
For each of 2,000 draws, I measure the spread in annualized geometric returns.

In development, the simulated spread is at least as large as the observed
2.65 points in **48%** of draws. Later, it exceeds the observed 3.77 points
in **87%** of draws. Neither spread is unusually large under this model.
Across 21-, 63- and 126-session blocks, those frequencies are 45–55% in
development and 87–90% later.

Equal expected returns are an assumption of this test, rather than a
conclusion from it. The observed spread gives me little reason to choose
the historical winner over a combination of schedules.

## More orders, similar traded notional
{: #what-it-takes-to-implement }

The trade-off is in execution. I have three books submitting smaller
orders, so their order counts add up while traded notional averages to
that of the standalone schedules. Here, two-way turnover means purchases
plus sales divided by strategy notional.

Over the later period, a single schedule averages about **2,429 orders a
year**, against **7,288** for three tranches. Two-way turnover averages
**18.83 times notional a year** in both cases. At USD 5 million total
notional, that means an average order of roughly USD 38,800 for one
schedule and USD 12,900 for three tranches.

The proportional cost deduction is therefore the same: **0.94 percentage
points a year** later and **1.29 points** in development, measured as the
annualized average of daily costs. With a proportional charge, the amount
traded determines the cost.

The comparison scales each standalone book to one third of its size and
charges costs to each book separately. Fixed ticket charges, borrow,
financing and market impact are outside the calculation. Zarattini and Pagani's
[tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
shows why the answer can change with portfolio size: smaller
orders can reduce impact, but minimum commissions can make the extra
tickets expensive.

## What I would keep

For Ridge, I prefer the three starting weeks under the proportional costs
used here. The Sharpe improvement is modest, especially after 2021, but it
comes with less dependence on a calendar I have little reason to favour
in advance. I'd rather accept the average across starting weeks than
commit the whole portfolio to one and risk ending up at the bottom of
the range.

## References

- Corey Hoffstein, Justin Sibears and Nathan Faber, *Rebalancing Timing Luck: The Difference between Hired and Fired*, summarized in [Newfound Research's rebalance timing luck overview](https://www.thinknewfound.com/rebalance-timing-luck).
- Carlo Zarattini and Alberto Pagani, [*The Tranching Dilemma: A Cost-Aware Approach to Mitigate Rebalance Timing Luck in Factor Portfolios*](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf), 14 November 2025 version, PDF pp. 9–12.

[^calibration]: Stock-volatility estimates are multiplied by 1.18 here, compared with 1.55 in the joint-sizing article. All fifteen calendars use the same multiplier.
