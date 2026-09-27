---
published: false
layout: post
title: "Combining Rebalance Weeks Reduces Timing Risk"
description: "The spread between rebalance schedules is luck. Three tranches remove most of it and lower volatility at the same average return."
date: 2025-05-10
last_modified_at: 2026-09-27
categories: ["Portfolio construction"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/rebalance-tranching
---

## The starting-week problem

The strategy rebalances every three weeks, which raises an awkward question:
which weeks? Picking a signal weekday and one of three starting weeks gives
fifteen schedules. They use the same forecasts and allocation rules and differ
only in the dates they trade on. Across them, annualized net return ranges
from **10.21% to 12.27%** over September 1998–May 2026, a **2.06-point spread**
from the calendar alone. How much of that is real, and what should I do about it?

I use the [same stock strategy](/quants/2026/08/29/portfolio-optimization.html)
throughout, with an earlier version of the Ridge ranking: the forecasts,
point-in-time universe, selection and sizing rules and gross exposure cap stay
fixed. The signal weekday is the day the schedule forms its portfolio;
execution is at the next close. All returns are after the 5 bp trading-cost
allowance, and I also report development (September 1998–December 2021) and
later history (January 2022–May 2026) separately.

## Is the spread more than luck?

The fifteen schedules are really one dimension: fifteen phases of a
fifteen-session cycle, so Friday of week 3 sits next to Monday of week 1. Their
daily returns are highly correlated, but not identical, and over 28 years small
differences in which days each schedule holds add up.

The test is simple. If no schedule is truly better, their daily returns share
one expectation. Resampling the demeaned daily returns in three-month blocks,
which keeps each day's correlation across schedules, shows the spread luck
alone produces: a median of **2.6 points**, and at least the observed 2.06 in
82% of draws. The observed spread is, if anything, smaller than typical luck.

Figure 1 shows how this looks in a plain grid. No weekday and no starting week
wins consistently, and schedules one session apart can differ by more than a
point: week 3 returns 11.49% on Wednesday, 10.21% on Thursday and 11.37% on
Friday.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/calendar-grid" mobile="/assets/tranching/calendar-grid_mobile" version="2" alt="Full-period annualized returns for three starting-week offsets and five signal weekdays, with five three-tranche portfolios below. Standalone returns range from 10.21% to 12.27%." %}
</div>


<p class="figure-caption"><strong>Figure 1: No weekday or starting week wins consistently.</strong> Annualized net return, September 1998–May 2026. Rows are starting weeks and columns signal weekdays; one colour scale. The separate bottom row combines the three starting weeks of each weekday.</p>

Shorter windows make luck look bigger, not smaller. Over January 2022–May 2026
the three Friday schedules return 5.42% to 9.91% (Figure 2), and all fifteen
span 5.13 points. That sounds dramatic, but in six consecutive windows of the
same length since 1998 the spread was 5.6 to 10.5 points: over any four or five
years, fixed schedules drift several points apart. In single years the spread
was 8 to 22 points.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/schedule-performance" mobile="/assets/tranching/schedule-performance_mobile" version="6" alt="January 2022–May 2026 Friday calendars: shaded band between fixed Week 2 and Week 3 paths, returning 9.91% and 5.42% annually. The three-tranche portfolio returns 8.02%." %}
</div>


<p class="figure-caption"><strong>Figure 2: Three schedules, one strategy.</strong> Friday schedules, 3 January 2022–27 May 2026. Shading joins the best and worst of the three starting weeks over this period; the blue line combines all three. The index compounds daily net P&amp;L per unit of fixed notional; endpoint labels give annualized geometric returns.</p>

So there is no best schedule to find. Picking the winner in the grid would be
fitting noise, and the only way to reduce dependence on it is to hold several.

## Three tranches

Each tranche receives one third of strategy notional, holds its own portfolio
and rebalances every three weeks, one week apart, so one tranche trades each
week (Table 1).

<table class="research-table sleeve-schedule">
  <caption><strong>Table 1: Two rotations over six weeks.</strong> W1–W6 denote weeks; ● marks a rebalance and — means hold.</caption>
  <thead><tr><th>Offset</th><th>W1</th><th>W2</th><th>W3</th><th>W4</th><th>W5</th><th>W6</th></tr></thead>
  <tbody>
    <tr class="sleeve-a"><th scope="row">Week 1 <small>⅓ notional</small></th><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td></tr>
    <tr class="sleeve-b"><th scope="row">Week 2 <small>⅓ notional</small></th><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td></tr>
    <tr class="sleeve-c"><th scope="row">Week 3 <small>⅓ notional</small></th><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td></tr>
  </tbody>
</table>

For daily net P&L per unit of fixed notional $r_{j,t}$, the combined return is

$$
r_{\mathrm{combined},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

Its arithmetic mean is exactly the average of the three schedules', costs
included, so tranching cannot raise expected return; its compounded return is
a few basis points higher only because volatility, and with it the
compounding drag, is lower.

## What tranching buys

Combining the three starting weeks of each weekday cuts the full-history spread
from 2.06 points across all fifteen schedules to **0.40** across the five
combined portfolios. The fairer comparison, across the five weekdays with the
starting week held fixed, gives 1.00, 1.46 and 2.06 points against the same
0.40, and the combined spread is narrower in every year from 1999 to 2025.

Volatility falls from **8.53% to 7.88%** on average, at the same gross exposure.
That is plain diversification: three books with daily correlation $\rho$
combine to $\sqrt{(1+2\rho)/3}$ of the single-book volatility, and with
$\rho\approx0.77$ in development that predicts an 8% reduction, as observed.
Later, with $\rho\approx0.84$, the reduction is smaller, about 5.5%. With the
same average return, Sharpe rises from 1.30 to 1.41 (Table 2 and Figure 3).

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Same average return, lower risk.</strong> Mean [minimum, maximum] across the fifteen single schedules or the five three-tranche portfolios. Brackets give the range across schedules. Net return is geometric; return, volatility and drawdown are percentages. Annualization uses 252 sessions and Sharpe a zero cash rate.</caption>
  <thead><tr><th>Metric</th><th>15 single<br>schedules</th><th>5 three-tranche<br>portfolios</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">Full history · September 1998–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>11.37<br>[10.21, 12.27]</td><td>11.43<br>[11.27, 11.67]</td></tr>
    <tr><th scope="row">Volatility</th><td>8.53<br>[8.42, 8.69]</td><td>7.88<br>[7.82, 7.90]</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.30<br>[1.19, 1.40]</td><td>1.41<br>[1.39, 1.44]</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−19.51<br>[−23.63, −14.51]</td><td>−16.82<br>[−18.58, −15.08]</td></tr>
    <tr class="period-heading"><th colspan="3">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Net return</th><td>12.04<br>[10.78, 13.08]</td><td>12.10<br>[11.87, 12.37]</td></tr>
    <tr><th scope="row">Volatility</th><td>8.38<br>[8.23, 8.56]</td><td>7.70<br>[7.62, 7.73]</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.40<br>[1.27, 1.53]</td><td>1.52<br>[1.50, 1.55]</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−19.51<br>[−23.63, −14.51]</td><td>−16.82<br>[−18.58, −15.08]</td></tr>
    <tr class="period-heading"><th colspan="3">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>7.87<br>[5.42, 10.55]</td><td>7.91<br>[7.25, 8.31]</td></tr>
    <tr><th scope="row">Volatility</th><td>9.31<br>[9.16, 9.41]</td><td>8.80<br>[8.74, 8.83]</td></tr>
    <tr><th scope="row">Sharpe</th><td>0.86<br>[0.62, 1.12]</td><td>0.91<br>[0.84, 0.95]</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−8.98<br>[−10.99, −7.39]</td><td>−8.61<br>[−8.83, −8.30]</td></tr>
  </tbody>
</table>

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/calendar-return-risk" mobile="/assets/tranching/calendar-return-risk_mobile" version="3" alt="Full-period mean and range across fifteen standalone calendars versus five three-tranche portfolios. Mean net return is 11.37% versus 11.43%; mean volatility is 8.53% versus 7.88%." %}
</div>


<p class="figure-caption"><strong>Figure 3: Same return, less dependence on the schedule and lower volatility.</strong> September 1998–May 2026. Each dot is the mean; each line spans the minimum and maximum across the fifteen single schedules or five three-tranche portfolios.</p>

[Concretum's tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
finds the same before costs: average return barely changes as tranches are
added, while dispersion across schedules shrinks. Its cost-aware result is the
caveat: with fixed commissions and market impact, the extra, smaller trades can
outweigh the benefit for small books.

## Trading costs
{: #what-it-takes-to-implement }

Tranching triples the number of trades but not the traded notional. At the same
USD 5 million reference notional, the later Friday comparison goes from about
2,807 orders a year for a single schedule to 8,420 for three tranches, with the
average order falling from about USD 44,000 to 14,700. Two-way traded notional
stays at 24.7 times notional a year, so under a proportional 5 bp cost the cost
drag is unchanged: 1.24 points a year later and 1.41 in development, charged
before any netting between tranches. Fixed ticket costs, borrow and financing
are outside this comparison, and they are exactly where Concretum's caveat
applies.

## What the schedule is worth

On this strategy, the choice of rebalance schedule moves annual return by about
2 points over 28 years and by several points over any four or five years, and
that spread is what luck alone would produce. Three tranches remove most of it
and lower volatility by 5 to 8% at the same average return, which makes them
the default I'd use.

Some questions stay open. Spreading over all fifteen schedules would lower
volatility a little further, to 7.73% with a Sharpe of 1.44: where do the
returns from more tranches stop being worth the extra books? Does the trading
controls' dependence on the previous portfolio make schedule luck larger for
this strategy than for a simpler one? And at what book size do fixed trading
costs make tranching a net cost?
