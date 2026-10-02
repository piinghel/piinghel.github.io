---
published: true
layout: post
interactive_charts: true
toc: true
title: "Reducing Rebalancing Luck"
description: "Combining Ridge rebalance schedules preserves mean return while reducing volatility and the risk of choosing an unlucky starting week."
date: 2025-05-10
last_modified_at: 2026-10-03
categories: ["Portfolio construction"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/rebalancing-luck.html
redirect_from:
  - /quants/2025/05/10/rebalancing-luck.html
home_after: _posts/2026-08-29-joint-sizing.md
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/rebalance-tranching
---

The allocation approach in [From Volatility Scaling to Joint Sizing]({% link _posts/2026-08-29-joint-sizing.md %})
rebalances every three weeks. That still leaves a starting date to choose: this
Friday, next Friday, or the Friday after. The model is the same in each case,
but a week's difference in timing can leave me with quite different returns.

In the other articles I calculate each schedule's metrics separately and
report their mean. Here I combine them, with one third of the notional in
each. I want lower volatility and a higher Sharpe ratio at the same average
return, with less dependence on picking a fortunate starting week.

[Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck)
and [Concretum's tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
discuss this approach to rebalance timing risk. Here I apply it to Ridge
and look at the benefit after trading costs.

## The starting week matters

Figure 1 shows the three Friday schedules from January 2022 to May 2026.
They use the same Ridge regression on 80 ranking predictors and the same
[joint sizing rules]({% link _posts/2026-08-29-joint-sizing.md %}),
including the rank buffer and trade penalty. Orders execute at the next
trading session's close after the signal date. All returns include 5 bp
per dollar traded. This comparison retains the earlier **1.18 volatility
multiplier**, versus the development-calibrated **1.55** in the
[joint-sizing article]({% link _posts/2026-08-29-joint-sizing.md %}#covariance-and-risk-forecasts);
both use a 7% forecast risk budget, so the portfolios here take more risk.

Over this period, annualized net return ranges from **5.73% to 8.95%**.
That is a 3.22 percentage point gap from choosing a different starting
week. Combining the three gives **7.70%**. I couldn't have known in advance
which week would win, and I wouldn't want the whole portfolio exposed to
the one that earned 5.73%.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="schedules" source="/assets/rebalancing-luck/ridge-paths.json?v=2" base="/assets/rebalancing-luck/ridge-paths" mobile="/assets/rebalancing-luck/ridge-paths_mobile" label="Net growth of three Friday rebalance schedules and their equal-notional combination, January 2022 to May 2026." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 1: Less dependence on one starting week.</strong> Friday signal schedules, January 2022–May 2026, indexed to 100 at the 31 December 2021 close, on a log scale. Grey lines show the individual schedules; blue combines them at one third of notional each. Each line compounds daily net P&amp;L per unit of fixed notional.</p>

## Split the portfolio across three weeks

I implement the combination as three separate books, or tranches, each
with one third of the total notional. Each still rebalances every
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
costs included. The slightly higher geometric return reflects the lower
volatility drag when compounding the combined daily returns. I keep total notional unchanged
throughout the comparison.

Sharpe needs a different calculation. The mean of three standalone Sharpe
ratios describes the average schedule; the Sharpe of the combined portfolio
uses the mean and volatility of its blended daily returns. That second
calculation captures the diversification between starting weeks.

## The diversification benefit

The three books use the same model at different dates, so their returns
are closely correlated without being identical. The reduction in volatility
follows directly from their covariance. For three books with the same
volatility $$\sigma$$ and pairwise correlation $$\rho$$,

$$
\sigma_{\mathrm{combined}}=\sigma\sqrt{\frac{1+2\rho}{3}}.
$$

The empirical question is how much risk this removes after costs.

To see how much this helps beyond Friday, I repeat the comparison for
every weekday. Three starting weeks across five weekdays give fifteen
single schedules and five combined portfolios. I report September
1998–December 2021, the development period, and January 2022–May 2026,
the later period, separately.

Table 2 shows the expected diversification benefit. Average volatility
falls from **8.75% to 8.15%** in development and from **9.65% to 9.26%**
later. Sharpe rises from **1.30 to 1.40** and **0.81 to 0.84**, respectively.
Average correlation between starting weeks is 0.80 in development and
0.88 later. The formula implies about 7% and 4% lower volatility,
respectively, almost exactly the reductions in the table. The books have
similar standalone volatilities, so the equal-volatility approximation
works well here.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Diversification improves Sharpe.</strong> Mean statistics across fifteen standalone schedules and five combined portfolios. Each combined portfolio first averages three schedules' daily returns; its statistics are then calculated and averaged across weekdays. Returns are geometric; return, volatility and drawdown are percentages. Annualization uses 252 sessions and Sharpe a zero cash rate.</caption>
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

A lower-volatility blend also leaves room for more notional at the same
risk level, subject to gross-exposure limits and financing costs.

## Less spread, more trading
{: #less-dependence-on-the-calendar }

I like how Figure 2 in [Concretum's study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf#page=10)
puts the reduction in timing luck beside the extra trading it requires.
The same comparison here stops at three tranches: one third rebalanced
each week is a practical cadence I would be comfortable with.

Going from one to two to three tranches brings the development return
spread from **2.65 to 1.83 to 1.26 percentage points**. Later, it falls
from **3.77 to 2.03 to 0.95 points**. By three, the observed spread has
roughly halved in development and fallen by three quarters later.
Order counts rise with each additional tranche.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="calendars" source="/assets/rebalancing-luck/ridge-calendars.json?v=4" base="/assets/rebalancing-luck/ridge-calendars" mobile="/assets/rebalancing-luck/ridge-calendars_mobile" label="Observed calendar return spread declines and annual order counts rise from one to three tranches, in development and the later period." version="4" %}
</div>
<p class="figure-caption"><strong>Figure 2: Less calendar spread, more orders.</strong> Range of annualized geometric net returns and mean annual order count across 15 single schedules, 15 pairs and five three-tranche portfolios. Each combination uses equal notional and a common weekday. Two tranches alternate one- and two-week rebalance gaps; three rebalance weekly. The ranges describe these calendar choices, whose number changes across the comparison.</p>

Weekly thirds remove the starting-week choice, but leave a weekday to
choose. Holding the number of weekday choices at five gives a useful
check: in development, the combined spread of **1.26 points** is narrower
than Week 2 and Week 3, but wider than Week 1's **1.03 points**. Later,
the combined **0.95 points** is below all three standalone weekday ranges
of **1.34–3.69 points**. The reduction in weekday sensitivity is therefore
more consistent in the later period.

## Putting the spread in context

A calendar that wins in a backtest might have a persistent advantage.
Before preferring it, though, I want to know how unusual the full spread
across the fifteen standalone calendars is.

The test assumes equal expected returns. I equalize the fifteen calendars'
arithmetic means and resample 63-session blocks of days,
using the same blocks for all fifteen calendars. This preserves their
dependence on one another and the sequence of returns within each block.
For each of 2,000 draws, I measure the spread in annualized geometric returns.

In development, the simulated spread is at least as large as the observed
2.65 points in **48%** of draws. Later, it exceeds the observed 3.77 points
in **87%** of draws. Neither spread is unusually large under this model.
Across 21-, 63- and 126-session blocks, those frequencies are 45–55% in
development and 87–90% later.

Under that assumption, the observed spread gives me little reason to choose
the historical winner over a combination of schedules.

## Smaller trades, more rebalance cycles
{: #what-it-takes-to-implement }

The execution changes as well. Three books submit smaller
orders, so their order counts add up while traded notional averages to
that of the standalone schedules. Here, two-way turnover means purchases
plus sales divided by strategy notional.

Over the later period, a single schedule averages about **2,429 orders a
year**, against **7,288** for three tranches. Two-way turnover averages
**18.83 times notional a year** for both the single and three-tranche
portfolios over that later period. Three times as many orders,
each about a third of the size, leaves the amount traded unchanged.

The proportional cost deduction is therefore the same: **0.94 percentage
points a year** later and **1.29 points** in development, measured as the
annualized average of daily costs. With a proportional charge, the amount
traded determines the cost.

Trading every week also means **three rebalance cycles instead of one**
over each three-week period. Each cycle needs execution oversight and
post-trade reconciliation, so operational work and costs can rise even
when total traded notional stays the same. These costs are outside the
5 bp charge; they do not necessarily triple with the number of rebalances.

For an institutional portfolio, the smaller trade size is another reason
to consider tranching. Rebalancing a third of the portfolio each week
spreads demand for liquidity across dates. At comparable liquidity and
execution horizons, smaller orders should reduce market impact. The
benefit depends on participation rates and how the original orders would
have been worked; splitting a rebalance into child orders already captures
some of it.

Zarattini and Pagani's [tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
examines both retail and institutional portfolio sizes. Minimum commissions
penalize its smallest accounts, while lower impact makes tranching more
attractive at larger sizes. My focus here is the latter setting. The 5 bp
charge holds costs proportional to traded notional, so the reported gains
come from diversification; any saving from lower market impact would be
additional. Borrow and financing are also outside the calculation.

## What I would keep

I would rebalance one third each week while keeping each book's three-week
holding cycle. That reduces the dependence on the starting week and
improves Sharpe in both periods, although the later improvement is modest.
I'd rather share the notional across starting weeks than
commit the whole portfolio to one and risk ending up at the bottom of
the range.

## References

- Corey Hoffstein, Justin Sibears and Nathan Faber, *Rebalancing Timing Luck: The Difference between Hired and Fired*, summarized in [Newfound Research's rebalance timing luck overview](https://www.thinknewfound.com/rebalance-timing-luck).
- Carlo Zarattini and Alberto Pagani, [*The Tranching Dilemma: A Cost-Aware Approach to Mitigate Rebalance Timing Luck in Factor Portfolios*](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf), 14 November 2025 version, PDF pp. 9–14.
